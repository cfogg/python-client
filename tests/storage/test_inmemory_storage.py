"""In-Memory storage test module."""
# pylint: disable=no-self-use
from splitio.models.splits import Split
from splitio.models.segments import Segment
from splitio.models.impressions import Impression
from splitio.models.events import Event, EventWrapper

from splitio.storage.inmemmory import InMemorySplitStorage, InMemorySegmentStorage, \
    InMemoryImpressionStorage, InMemoryEventStorage, InMemoryTelemetryStorage


class InMemorySplitStorageTests(object):
    """In memory split storage test cases."""

    def test_storing_retrieving_splits(self, mocker):
        """Test storing and retrieving splits works."""
        storage = InMemorySplitStorage()

        split = mocker.Mock(spec=Split)
        name_property = mocker.PropertyMock()
        name_property.return_value = 'some_split'
        type(split).name = name_property

        storage.put(split)
        assert storage.get('some_split') == split
        assert storage.get_split_names() == ['some_split']
        assert storage.get_all_splits() == [split]
        assert storage.get('nonexistant_split') is None

        storage.remove('some_split')
        assert storage.get('some_split') is None

    def test_get_splits(self, mocker):
        """Test retrieving a list of passed splits."""
        split1 = mocker.Mock()
        name1_prop = mocker.PropertyMock()
        name1_prop.return_value = 'split1'
        type(split1).name = name1_prop
        split2 = mocker.Mock()
        name2_prop = mocker.PropertyMock()
        name2_prop.return_value = 'split2'
        type(split2).name = name2_prop

        storage = InMemorySplitStorage()
        storage.put(split1)
        storage.put(split2)

        splits = storage.fetch_many(['split1', 'split2', 'split3'])
        assert len(splits) == 3
        assert splits['split1'].name == 'split1'
        assert splits['split2'].name == 'split2'
        assert 'split3' in splits

    def test_store_get_changenumber(self):
        """Test that storing and retrieving change numbers works."""
        storage = InMemorySplitStorage()
        assert storage.get_change_number() == -1
        storage.set_change_number(5)
        assert storage.get_change_number() == 5

    def test_get_split_names(self, mocker):
        """Test retrieving a list of all split names."""
        split1 = mocker.Mock()
        name1_prop = mocker.PropertyMock()
        name1_prop.return_value = 'split1'
        type(split1).name = name1_prop
        split2 = mocker.Mock()
        name2_prop = mocker.PropertyMock()
        name2_prop.return_value = 'split2'
        type(split2).name = name2_prop

        storage = InMemorySplitStorage()
        storage.put(split1)
        storage.put(split2)

        assert set(storage.get_split_names()) == set(['split1', 'split2'])

    def test_get_all_splits(self, mocker):
        """Test retrieving a list of all split names."""
        split1 = mocker.Mock()
        name1_prop = mocker.PropertyMock()
        name1_prop.return_value = 'split1'
        type(split1).name = name1_prop
        split2 = mocker.Mock()
        name2_prop = mocker.PropertyMock()
        name2_prop.return_value = 'split2'
        type(split2).name = name2_prop

        storage = InMemorySplitStorage()
        storage.put(split1)
        storage.put(split2)

        all_splits = storage.get_all_splits()
        assert next(s for s in all_splits if s.name == 'split1')
        assert next(s for s in all_splits if s.name == 'split2')

    def test_is_valid_traffic_type(self, mocker):
        """Test that traffic type validation works properly."""
        split1 = mocker.Mock()
        name1_prop = mocker.PropertyMock()
        name1_prop.return_value = 'split1'
        type(split1).name = name1_prop
        split2 = mocker.Mock()
        name2_prop = mocker.PropertyMock()
        name2_prop.return_value = 'split2'
        type(split2).name = name2_prop
        split3 = mocker.Mock()
        tt_user = mocker.PropertyMock()
        tt_user.return_value = 'user'
        tt_account = mocker.PropertyMock()
        tt_account.return_value = 'account'
        name3_prop = mocker.PropertyMock()
        name3_prop.return_value = 'split3'
        type(split3).name = name3_prop
        type(split1).traffic_type_name = tt_user
        type(split2).traffic_type_name = tt_account
        type(split3).traffic_type_name = tt_user

        storage = InMemorySplitStorage()

        storage.put(split1)
        assert storage.is_valid_traffic_type('user') is True
        assert storage.is_valid_traffic_type('account') is False

        storage.put(split2)
        assert storage.is_valid_traffic_type('user') is True
        assert storage.is_valid_traffic_type('account') is True

        storage.put(split3)
        assert storage.is_valid_traffic_type('user') is True
        assert storage.is_valid_traffic_type('account') is True

        storage.remove('split1')
        assert storage.is_valid_traffic_type('user') is True
        assert storage.is_valid_traffic_type('account') is True

        storage.remove('split2')
        assert storage.is_valid_traffic_type('user') is True
        assert storage.is_valid_traffic_type('account') is False

        storage.remove('split3')
        assert storage.is_valid_traffic_type('user') is False
        assert storage.is_valid_traffic_type('account') is False

    def test_traffic_type_inc_dec_logic(self, mocker):
        """Test that adding/removing split, handles traffic types correctly."""
        storage = InMemorySplitStorage()

        split1 = mocker.Mock()
        name1_prop = mocker.PropertyMock()
        name1_prop.return_value = 'split1'
        type(split1).name = name1_prop

        split2 = mocker.Mock()
        name2_prop = mocker.PropertyMock()
        name2_prop.return_value = 'split1'
        type(split2).name = name2_prop

        tt_user = mocker.PropertyMock()
        tt_user.return_value = 'user'

        tt_account = mocker.PropertyMock()
        tt_account.return_value = 'account'

        type(split1).traffic_type_name = tt_user
        type(split2).traffic_type_name = tt_account

        storage.put(split1)
        assert storage.is_valid_traffic_type('user') is True
        assert storage.is_valid_traffic_type('account') is False

        storage.put(split2)
        assert storage.is_valid_traffic_type('user') is False
        assert storage.is_valid_traffic_type('account') is True

    def test_kill_locally(self):
        """Test kill local."""
        storage = InMemorySplitStorage()

        split = Split('some_split', 123456789, False, 'some', 'traffic_type',
                      'ACTIVE', 1)
        storage.put(split)
        storage.set_change_number(1)

        storage.kill_locally('test', 'default_treatment', 2)
        assert storage.get('test') is None

        storage.kill_locally('some_split', 'default_treatment', 0)
        assert storage.get('some_split').change_number == 1
        assert storage.get('some_split').killed is False
        assert storage.get('some_split').default_treatment == 'some'

        storage.kill_locally('some_split', 'default_treatment', 3)
        assert storage.get('some_split').change_number == 3


class InMemorySegmentStorageTests(object):
    """In memory segment storage tests."""

    def test_segment_storage_retrieval(self, mocker):
        """Test storing and retrieving segments."""
        storage = InMemorySegmentStorage()
        segment = mocker.Mock(spec=Segment)
        name_property = mocker.PropertyMock()
        name_property.return_value = 'some_segment'
        type(segment).name = name_property

        storage.put(segment)
        assert storage.get('some_segment') == segment
        assert storage.get('nonexistant-segment') is None

    def test_change_number(self, mocker):
        """Test storing and retrieving segment changeNumber."""
        storage = InMemorySegmentStorage()
        storage.set_change_number('some_segment', 123)
        # Change number is not updated if segment doesn't exist
        assert storage.get_change_number('some_segment') is None
        assert storage.get_change_number('nonexistant-segment') is None

        # Change number is updated if segment does exist.
        storage = InMemorySegmentStorage()
        segment = mocker.Mock(spec=Segment)
        name_property = mocker.PropertyMock()
        name_property.return_value = 'some_segment'
        type(segment).name = name_property
        storage.put(segment)
        storage.set_change_number('some_segment', 123)
        assert storage.get_change_number('some_segment') == 123

    def test_segment_contains(self, mocker):
        """Test using storage to determine whether a key belongs to a segment."""
        storage = InMemorySegmentStorage()
        segment = mocker.Mock(spec=Segment)
        name_property = mocker.PropertyMock()
        name_property.return_value = 'some_segment'
        type(segment).name = name_property
        storage.put(segment)

        storage.segment_contains('some_segment', 'abc')
        assert segment.contains.mock_calls[0] == mocker.call('abc')

    def test_segment_update(self):
        """Test updating a segment."""
        storage = InMemorySegmentStorage()
        segment = Segment('some_segment', ['key1', 'key2', 'key3'], 123)
        storage.put(segment)
        assert storage.get('some_segment') == segment

        storage.update('some_segment', ['key4', 'key5'], ['key2', 'key3'], 456)
        assert storage.segment_contains('some_segment', 'key1')
        assert storage.segment_contains('some_segment', 'key4')
        assert storage.segment_contains('some_segment', 'key5')
        assert not storage.segment_contains('some_segment', 'key2')
        assert not storage.segment_contains('some_segment', 'key3')
        assert storage.get_change_number('some_segment') == 456


class InMemoryImpressionsStorageTests(object):
    """InMemory impressions storage test cases."""

    def test_push_pop_impressions(self):
        """Test pushing and retrieving impressions."""
        storage = InMemoryImpressionStorage(100)
        storage.put([Impression('key1', 'feature1', 'on', 'l1', 123456, 'b1', 321654)])
        storage.put([Impression('key2', 'feature1', 'on', 'l1', 123456, 'b1', 321654)])
        storage.put([Impression('key3', 'feature1', 'on', 'l1', 123456, 'b1', 321654)])

        # Assert impressions are retrieved in the same order they are inserted.
        assert storage.pop_many(1) == [
            Impression('key1', 'feature1', 'on', 'l1', 123456, 'b1', 321654)
        ]
        assert storage.pop_many(1) == [
            Impression('key2', 'feature1', 'on', 'l1', 123456, 'b1', 321654)
        ]
        assert storage.pop_many(1) == [
            Impression('key3', 'feature1', 'on', 'l1', 123456, 'b1', 321654)
        ]

        # Assert inserting multiple impressions at once works and maintains order.
        impressions = [
            Impression('key1', 'feature1', 'on', 'l1', 123456, 'b1', 321654),
            Impression('key2', 'feature1', 'on', 'l1', 123456, 'b1', 321654),
            Impression('key3', 'feature1', 'on', 'l1', 123456, 'b1', 321654)
        ]
        assert storage.put(impressions)

        # Assert impressions are retrieved in the same order they are inserted.
        assert storage.pop_many(1) == [
            Impression('key1', 'feature1', 'on', 'l1', 123456, 'b1', 321654)
        ]
        assert storage.pop_many(1) == [
            Impression('key2', 'feature1', 'on', 'l1', 123456, 'b1', 321654)
        ]
        assert storage.pop_many(1) == [
            Impression('key3', 'feature1', 'on', 'l1', 123456, 'b1', 321654)
        ]

    def test_queue_full_hook(self, mocker):
        """Test queue_full_hook is executed when the queue is full."""
        storage = InMemoryImpressionStorage(100)
        queue_full_hook = mocker.Mock()
        storage.set_queue_full_hook(queue_full_hook)
        impressions = [
            Impression('key%d' % i, 'feature1', 'on', 'l1', 123456, 'b1', 321654)
            for i in range(0, 101)
        ]
        storage.put(impressions)
        assert queue_full_hook.mock_calls == mocker.call()

    def test_clear(self):
        """Test clear method."""
        storage = InMemoryImpressionStorage(100)
        storage.put([Impression('key1', 'feature1', 'on', 'l1', 123456, 'b1', 321654)])

        assert storage._impressions.qsize() == 1
        storage.clear()
        assert storage._impressions.qsize() == 0


class InMemoryEventsStorageTests(object):
    """InMemory events storage test cases."""

    def test_push_pop_events(self):
        """Test pushing and retrieving events."""
        storage = InMemoryEventStorage(100)
        storage.put([EventWrapper(
            event=Event('key1', 'user', 'purchase', 3.5, 123456, None),
            size=1024,
        )])
        storage.put([EventWrapper(
            event=Event('key2', 'user', 'purchase', 3.5, 123456, None),
            size=1024,
        )])
        storage.put([EventWrapper(
            event=Event('key3', 'user', 'purchase', 3.5, 123456, None),
            size=1024,
        )])

        # Assert impressions are retrieved in the same order they are inserted.
        assert storage.pop_many(1) == [Event('key1', 'user', 'purchase', 3.5, 123456, None)]
        assert storage.pop_many(1) == [Event('key2', 'user', 'purchase', 3.5, 123456, None)]
        assert storage.pop_many(1) == [Event('key3', 'user', 'purchase', 3.5, 123456, None)]

        # Assert inserting multiple impressions at once works and maintains order.
        events = [
            EventWrapper(
                event=Event('key1', 'user', 'purchase', 3.5, 123456, None),
                size=1024,
            ),
            EventWrapper(
                event=Event('key2', 'user', 'purchase', 3.5, 123456, None),
                size=1024,
            ),
            EventWrapper(
                event=Event('key3', 'user', 'purchase', 3.5, 123456, None),
                size=1024,
            ),
        ]
        assert storage.put(events)

        # Assert events are retrieved in the same order they are inserted.
        assert storage.pop_many(1) == [Event('key1', 'user', 'purchase', 3.5, 123456, None)]
        assert storage.pop_many(1) == [Event('key2', 'user', 'purchase', 3.5, 123456, None)]
        assert storage.pop_many(1) == [Event('key3', 'user', 'purchase', 3.5, 123456, None)]

    def test_queue_full_hook(self, mocker):
        """Test queue_full_hook is executed when the queue is full."""
        storage = InMemoryEventStorage(100)
        queue_full_hook = mocker.Mock()
        storage.set_queue_full_hook(queue_full_hook)
        events = [EventWrapper(event=Event('key%d' % i, 'user', 'purchase', 12.5, 321654, None), size=1024) for i in range(0, 101)]
        storage.put(events)
        assert queue_full_hook.mock_calls == [mocker.call()]

    def test_queue_full_hook_properties(self, mocker):
        """Test queue_full_hook is executed when the queue is full regarding properties."""
        storage = InMemoryEventStorage(200)
        queue_full_hook = mocker.Mock()
        storage.set_queue_full_hook(queue_full_hook)
        events = [EventWrapper(event=Event('key%d' % i, 'user', 'purchase', 12.5, 1, None),  size=32768) for i in range(160)]
        storage.put(events)
        assert queue_full_hook.mock_calls == [mocker.call()]

    def test_clear(self):
        """Test clear method."""
        storage = InMemoryEventStorage(100)
        storage.put([EventWrapper(
            event=Event('key1', 'user', 'purchase', 3.5, 123456, None),
            size=1024,
        )])

        assert storage._events.qsize() == 1
        storage.clear()
        assert storage._events.qsize() == 0


class InMemoryTelemetryStorageTests(object):
    """In-Memory telemetry storage unit tests."""

    def test_latencies(self):
        """Test storing and retrieving latencies."""
        storage = InMemoryTelemetryStorage()
        storage.inc_latency('sdk.get_treatment', -1)
        storage.inc_latency('sdk.get_treatment', 0)
        storage.inc_latency('sdk.get_treatment', 1)
        storage.inc_latency('sdk.get_treatment', 5)
        storage.inc_latency('sdk.get_treatment', 5)
        storage.inc_latency('sdk.get_treatment', 22)
        latencies = storage.pop_latencies()
        assert latencies['sdk.get_treatment'][0] == 1
        assert latencies['sdk.get_treatment'][1] == 1
        assert latencies['sdk.get_treatment'][5] == 2
        assert len(latencies['sdk.get_treatment']) == 22
        assert storage.pop_latencies() == {}

    def test_counters(self):
        """Test storing and retrieving counters."""
        storage = InMemoryTelemetryStorage()
        storage.inc_counter('some_counter_1')
        storage.inc_counter('some_counter_1')
        storage.inc_counter('some_counter_1')
        storage.inc_counter('some_counter_2')
        counters = storage.pop_counters()
        assert counters['some_counter_1'] == 3
        assert counters['some_counter_2'] == 1
        assert storage.pop_counters() == {}

    def test_gauges(self):
        """Test storing and retrieving gauges."""
        storage = InMemoryTelemetryStorage()
        storage.put_gauge('some_gauge_1', 321)
        storage.put_gauge('some_gauge_2', 654)
        gauges = storage.pop_gauges()
        assert gauges['some_gauge_1'] == 321
        assert gauges['some_gauge_2'] == 654
        assert storage.pop_gauges() == {}

    def test_clear(self):
        """Test clear."""
        storage = InMemoryTelemetryStorage()
        storage.put_gauge('some_gauge_1', 321)
        storage.inc_counter('some_counter_1')
        storage.inc_latency('sdk.get_treatment', 5)

        assert len(storage._counters) == 1
        assert len(storage._gauges) == 1
        assert len(storage._latencies) == 1

        storage.clear()

        assert len(storage._counters) == 0
        assert len(storage._gauges) == 0
        assert len(storage._latencies) == 0
