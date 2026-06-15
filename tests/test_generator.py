from scripts.generate_logs import gen_event


def test_gen_event_keys():
    e = gen_event()
    assert isinstance(e, dict)
    for k in ("timestamp","event_type","user","src_ip","dst_ip","message","severity"):
        assert k in e
    assert e['severity'] in ("INFO","MEDIUM","HIGH")
