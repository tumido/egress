"""Uni test suite for egress.task."""
import egress


def test_run_task(mocker):
    """Test the main task executor flow."""
    spark_context = mocker.MagicMock()
    get_local_spark_context = mocker.patch.object(
        egress.task, 'get_local_spark_context',
        return_value=spark_context
    )
    fetch_postgres_data = mocker.patch.object(
        egress.task, 'fetch_postgres_data', return_value=[]
    )
    push_to_ceph = mocker.patch.object(egress.task, 'push_to_ceph')

    egress.run_task()

    assert get_local_spark_context.called_once
    assert fetch_postgres_data.called_once
    assert push_to_ceph.called_once_with(spark_context, [])
