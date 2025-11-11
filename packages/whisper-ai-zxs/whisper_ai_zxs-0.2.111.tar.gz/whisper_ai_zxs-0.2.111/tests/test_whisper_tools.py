from whisper_ai_zxs.whisper_tools import WhisperTools_QYWX, WhisperTools_OrderManageTools


def test_get_group_info():
    qywx = WhisperTools_QYWX()
    group_name = qywx._get_group_name("wru252DAAAqRwvzxPdi0AbiIghCxGEHQ")
    print("group_name:", group_name)
    user_name = qywx._get_user_name("wmu252DAAAW5_g9R2KERY55kzyifRaOQ")
    print("user_name:", user_name)
    user_name = qywx._get_user_name("zhizhushou")
    print("user_name:", user_name)
    group_name = qywx._get_group_name("wmu252DAAAW5_g9R2KERY55kzyifRaOQ")
    print("group_name:", group_name)
    group_name = qywx._get_group_name("wru252DAAA7hHieFuCbX8KuiKYlddPXw")
    print("group_name:", group_name)
    group_name = qywx._get_group_name("wru252DAAA7FJV4O3baZDp0ndETmWJow")
    print("group_name:", group_name)
    group_name = qywx._get_group_name("wru252DAAAlv7973vdMX2-KKe8ikGLUQ")
    print("group_name:", group_name)
    group_name = qywx._get_group_name("wru252DAAAr9wNvHbjHRhKuEVrYE90iQ")
    print("group_name:", group_name)


def test_whisper_tools_QYWX():
    qywx = WhisperTools_QYWX()
    reply = qywx.get_reply_msg()
    print("reply:", reply)
    assert reply is not None

    qywx.set_reply_sended("1")

def test_get_reply_msg():
    qywx = WhisperTools_QYWX()
    reply = qywx.get_reply_msg()
    print("reply:", reply)
    assert reply is not None

def test_get_action_msg():
    qywx = WhisperTools_QYWX()
    reply = qywx.get_action_msg()
    print("reply:", reply)
    assert reply is not None

def test_add_reply_sended():
    qywx = WhisperTools_QYWX()
    qywx.add_reply_msg("测试群不存在的群", "text", "Test reply message！", "reply")

def test_add_action_msg():
    qywx = WhisperTools_QYWX()
    qywx.add_action_msg("Test action message！", "wx_scan_login") 
    qywx.add_action_msg("Test action message！", "wx_scan_order_download") 
    qywx.add_action_msg("Test action message！", "wdt_scan_download") 

def test_WhisperTools_OrderManageTools():
    tools = WhisperTools_OrderManageTools()
    order_info = tools.upload_file_format("/Users/lizhenhua/WhisperProjects/WhisperAI/tests/data/旺店通手工建单导入工具v6.0（for机器人）.xlsm")


def test_refresh_group_name():
    qywx = WhisperTools_QYWX()
    to_name = qywx.refresh_group_name("wru252DAAAbKgIJf8LgjJ5-jdeyBTP2A")
    print("to_name:", to_name)        

def test_upload_order_file_to_ERP():
    tools = WhisperTools_OrderManageTools()
    tools.upload_order_file_to_ERP("tests/data/旺店通导单(RPA)_new.xlsx")