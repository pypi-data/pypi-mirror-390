"""测试数据模型"""

from gateway_sdk.models import PrefabCall, PrefabResult, CallStatus, StreamEvent, StreamEventType


def test_prefab_call():
    """测试 PrefabCall"""
    call = PrefabCall(
        prefab_id="test-prefab",
        version="1.0.0",
        function_name="test_func",
        parameters={"key": "value"}
    )
    
    assert call.prefab_id == "test-prefab"
    assert call.version == "1.0.0"
    assert call.function_name == "test_func"
    assert call.parameters == {"key": "value"}
    
    # 测试 to_dict
    data = call.to_dict()
    assert data["prefab_id"] == "test-prefab"
    assert data["inputs"]["parameters"] == {"key": "value"}


def test_prefab_result():
    """测试 PrefabResult"""
    result = PrefabResult(
        status=CallStatus.SUCCESS,
        output={"result": {"data": "test"}},
        job_id="job-123"
    )
    
    assert result.is_success()
    assert result.get_result() == {"data": "test"}
    assert result.get("result") == {"data": "test"}
    assert result.get("nonexistent", "default") == "default"


def test_stream_event():
    """测试 StreamEvent"""
    event_data = {
        "type": "content",
        "data": "Hello"
    }
    
    event = StreamEvent.from_dict(event_data)
    assert event.type == StreamEventType.CONTENT
    assert event.data == "Hello"

