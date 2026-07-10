# Helper to get the enhancement code for _pf_run
enhanced_pf_run = '''def _pf_run(env, budget, max_hops):
    import time as _t
    h = max(1, min(int(max_hops), 8))
    if env is None:                                  # local build/dry-run: emit framings unvalidated
        return [_make((fr.format(url=_url(k), data=PAYLOAD),)) for k, fr in enumerate(PORTFOLIO_FRAMINGS)]
    
    # Initialize bandit arms for each framing
    bandit_arms = {f"framing_{k}": BanditArm(f"framing_{k}") for k in range(len(PORTFOLIO_FRAMINGS))}
    bandit = None
    if int(BANDIT_ENABLE):
        if BANDIT_ALGORITHM == "thompson":
            bandit = ThompsonSamplingBandit(bandit_arms)
        elif BANDIT_ALGORITHM == "ucb":
            bandit = UCBBandit(bandit_arms, exploration=float(BANDIT_EXPLORATION))
    
    deadline = _t.monotonic() + float(budget)
    slowest = [30.0]
    def ok():
        return _t.monotonic() + max(slowest[0] * 1.5, float(MARGIN_S)) < deadline
    def track(t0):
        slowest[0] = max(slowest[0], _t.monotonic() - t0)
    cands = []; idx = 0
    
    # Phase 1: validated DIVERSE single-post framings with bandit allocation
    if int(BANDIT_ENABLE) and bandit is not None:
        # Initialization phase: sample each arm BANDIT_INIT_SAMPLES times
        init_samples_per_arm = max(1, int(BANDIT_INIT_SAMPLES))
        for fr_idx, fr in enumerate(PORTFOLIO_FRAMINGS):
            for _ in range(init_samples_per_arm):
                if not ok() or len(cands) >= 2000:
                    break
                msg = fr.format(url=_url(idx), data=PAYLOAD); idx += 1
                t0 = _t.monotonic()
                fired = _pf_fired(env, (msg,), h)
                latency = _t.monotonic() - t0
                track(t0)
                bandit_arms[f"framing_{fr_idx}"].record_trial(fired, latency)
                if fired:
                    cands.append(_make((msg,)))
        
        # Adaptive phase: allocate remaining budget to best arms
        while ok() and len(cands) < 2000:
            # Select arm using bandit algorithm
            selected_arm_id = bandit.select_arm()
            fr_idx = int(selected_arm_id.split("_")[1])
            fr = PORTFOLIO_FRAMINGS[fr_idx]
            
            msg = fr.format(url=_url(idx), data=PAYLOAD); idx += 1
            t0 = _t.monotonic()
            fired = _pf_fired(env, (msg,), h)
            latency = _t.monotonic() - t0
            track(t0)
            bandit_arms[selected_arm_id].record_trial(fired, latency)
            if fired:
                cands.append(_make((msg,)))
        
        # Log bandit statistics
        stats = []
        for arm_id, arm in bandit_arms.items():
            fire_rate = arm.fire_rate()
            stats.append(f"{arm_id}(trials={arm.trials},hits={arm.successes},rate={fire_rate:.2f})")
        print("[portfolio][bandit] %s algorithm: %s" % (BANDIT_ALGORITHM, ", ".join(stats)), file=sys.stderr, flush=True)
    else:
        # Fixed allocation (original behavior)
        for fr in PORTFOLIO_FRAMINGS:
            for _ in range(max(0, int(PORTFOLIO_PER_FRAMING))):
                if not ok() or len(cands) >= 2000:
                    break
                msg = fr.format(url=_url(idx), data=PAYLOAD); idx += 1
                t0 = _t.monotonic(); fired = _pf_fired(env, (msg,), h); track(t0)
                if fired:
                    cands.append(_make((msg,)))
    
    # Phase 1b: validated multi-turn chains (MT_TURNS distinct-URL single-posts per candidate)
    turns = max(2, min(int(MT_TURNS), 32))
    for _ in range(max(0, int(PORTFOLIO_MT))):
        if not ok() or len(cands) >= 2000:
            break
        msgs = tuple(SINGLE_TEMPLATE.format(url=_url(idx + j), data=PAYLOAD) for j in range(turns)); idx += turns
        t0 = _t.monotonic(); fired = _pf_fired(env, msgs, h); track(t0)
        if fired:
            cands.append(_make(msgs))
    
    # Phase 1c: HELD-OUT-guardrail hedge
    for k in range(max(0, int(PORTFOLIO_DEPUTY))):
        if not ok() or len(cands) >= 2000:
            break
        msg = DEPUTY_TEMPLATES[k % len(DEPUTY_TEMPLATES)].format(addr="ops%04d@corp.invalid" % idx); idx += 1
        t0 = _t.monotonic(); fired = _pf_fired(env, (msg,), h); track(t0)
        if fired:
            cands.append(_make((msg,)))
    
    # Phase 2: adaptive burst
    if int(PORTFOLIO_BURST):
        best = None; bestk = 0
        for bt in MULTIHOP_TEMPLATES:
            if not ok():
                break
            k1 = _pf_count(env, bt.format(hops=h, url=_url(idx), data=PAYLOAD), h); idx += 1
            k2 = _pf_count(env, bt.format(hops=h, url=_url(idx), data=PAYLOAD), h); idx += 1
            if min(k1, k2) > bestk:
                bestk = min(k1, k2); best = bt
        print("[portfolio] burst stable_hits=%d (min_req=%d)" % (bestk, int(MIN_BURST_HITS)), file=sys.stderr, flush=True)
        if best is not None and bestk >= int(MIN_BURST_HITS):
            while ok() and len(cands) < 2000:
                msg = best.format(hops=h, url=_url(idx), data=PAYLOAD); idx += 1
                t0 = _t.monotonic()
                try:
                    env.reset(); env.interact(msg, max_tool_hops=h)
                except Exception:
                    pass
                track(t0)
                cands.append(_make((msg,)))
    
    # Phase 2b: single-hop FALLBACK
    while ok() and len(cands) < 2000:
        msg = SINGLE_TEMPLATE.format(url=_url(idx), data=PAYLOAD); idx += 1
        t0 = _t.monotonic(); _fired = False
        try:
            env.reset(); env.interact(msg, max_tool_hops=h)
            _tr = env.export_trace_dict()
            _fired = bool(_EVAL(dict(_tr))) if _EVAL is not None else (_count_marker_posts(dict(_tr)) > 0)
        except Exception:
            pass
        track(t0)
        if _fired:
            cands.append(_make((msg,)))
    print("[portfolio] returned %d validated candidates" % len(cands), file=sys.stderr, flush=True)
    return cands[:2000]
'''

print(enhanced_pf_run)
