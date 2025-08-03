from pyflink.datastream import StreamExecutionEnvironment, TimeCharacteristic
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream.window import EventTimeSessionWindows
from pyflink.common import Duration, WatermarkStrategy, Time
from pyflink.common.watermark_strategy import TimestampAssigner
import json

def create_env():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    env.set_stream_time_characteristic(TimeCharacteristic.EventTime)
    return env

def parse_event(json_str):
    try:
        event = json.loads(json_str)
        return (
            event.get("session_id", ""),
            event.get("received_at", 0),
            event.get("entry_page", None),
            event.get("exit_page", None),
            event.get("time_on_page", 0),
            event.get("scroll_depth", 0),
            event.get("page_url", None)
        )
    except json.JSONDecodeError:
        return ("", 0, None, None, 0, 0, None)

def format_session_output(session):
    session_id, values = session
    timestamps = [v[0] for v in values]
    entry_pages = [v[1] for v in values if v[1]]
    exit_pages = [v[2] for v in values if v[2]]
    total_time = sum(v[3] for v in values)
    max_scroll = max(v[4] for v in values)
    pages = [v[5] for v in values]

    return json.dumps({
        "session_id": session_id,
        "entry_page": entry_pages[0] if entry_pages else None,
        "exit_page": exit_pages[-1] if exit_pages else (pages[-1] if pages else None),
        "total_time_on_site": total_time,
        "max_scroll_depth": max_scroll,
        "total_pages_viewed": len(set(pages))
    })

class EventTimestampAssigner(TimestampAssigner):
    def extract_timestamp(self, value, record_timestamp):
        return value[1]  # Use received_at as the event timestamp (in milliseconds)

def main():
    env = create_env()

    kafka_source = FlinkKafkaConsumer(
        topics='sessions-stream',
        deserialization_schema=SimpleStringSchema(),
        properties={
            'bootstrap.servers': 'kafka:9092',
            'group.id': 'flink-session-consumer'
        }
    )

    kafka_sink = FlinkKafkaProducer(
        topic='aggregated-sessions',
        serialization_schema=SimpleStringSchema(),
        producer_config={'bootstrap.servers': 'kafka:9092'}
    )

    ds = env.add_source(kafka_source) \
        .map(parse_event, output_type=Types.TUPLE([
            Types.STRING(), Types.LONG(), Types.STRING(), Types.STRING(), Types.FLOAT(), Types.FLOAT(), Types.STRING()
        ])) \
        .assign_timestamps_and_watermarks(
            WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_seconds(5))
                            .with_timestamp_assigner(EventTimestampAssigner())
        ) \
        .key_by(lambda x: x[0]) \
        .window(EventTimeSessionWindows.with_gap(Time.seconds(30))) \
        .apply(
            lambda key, window, records, out: out.collect((key, list(records))),
            output_type=Types.TUPLE([Types.STRING(), Types.LIST(Types.TUPLE([
                Types.LONG(), Types.STRING(), Types.STRING(), Types.FLOAT(), Types.FLOAT(), Types.STRING()
            ]))])
        ) \
        .map(format_session_output, output_type=Types.STRING())

    ds.add_sink(kafka_sink)

    env.execute("Session Aggregator Job")

if __name__ == '__main__':
    main()