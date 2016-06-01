import jiffybox.api


def test_meta():
    p = jiffybox.api.Plan({
        u'cpus': 8,
        u'diskSizeInMB': 768000,
        u'id': 48,
        u'name': u'CloudLevel 5',
        u'priceCap': 69.99,
        u'pricePerHour': 0.11,
        u'pricePerHourFrozen': 0.03,
        u'ramInMB': 16384
    })
    assert p.cpus == 8
    assert p.diskSizeInMB == 768000
    assert p.id == 48
    assert p.name == 'CloudLevel 5'
    assert p.priceCap == 69.99
    assert p.pricePerHour == 0.11
    assert p.pricePerHourFrozen == 0.03
    assert p.ramInMB == 16384
