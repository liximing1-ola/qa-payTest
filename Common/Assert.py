"""
封装assert方法
"""
import json
from Common import logs
from Common import consts


def assert_code(code, expected_code, res):
    """
    验证response状态码
    :param res:
    :param code:
    :param expected_code:
    :return:
    """
    try:
        assert code == expected_code
        return True
    except:
        consts.fail_case_reason.append(res)
        raise


def assert_body(body, body_msg, expected_msg, res):
    """
    验证response body中任意属性的值
    :param res:
    :param body:
    :param body_msg:
    :param expected_msg:
    :return:
    """
    try:
        msg = body[body_msg]
        assert msg == expected_msg
        return True
    except:
        consts.fail_case_reason.append(res)
        raise


def assert_in_text(body, expected_msg):
    """
    验证response body中是否包含预期字符串
    :param body:
    :param expected_msg:
    :return:
    """
    try:
        text = json.dumps(body, ensure_ascii=False)
        assert expected_msg in text
        return True
    except:
        logs.get_log('assert.log').error("Response body Does not contain expected_msg, expected_msg is %s"
                                                 % expected_msg)
        Consts.RESULT_LIST.append('fail')
        raise


def assert_text(body, expected_msg):
    """
    验证response body中是否等于预期字符串
    :param body:
    :param expected_msg:
    :return:
    """
    try:
        assert body == expected_msg
        return True
    except:
        logs.get_log('assert.log').error("Response body != expected_msg, expected_msg is %s, body is %s"
                                              % (expected_msg, body))
        Consts.RESULT_LIST.append('fail')
        raise


def assert_time(time, expected_time):
    """
    验证response body响应时间小于预期最大响应时间,单位：毫秒
    :param time:
    :param expected_time:
    :return:
    """
    try:
        assert time < expected_time
        return True
    except:
        logs.get_log('assert.log').error("Response time > expected_time, expected_time is %s, time is %s"
                                              % (expected_time, time))
        Consts.RESULT_LIST.append('fail')
        raise


def assert_len(body, body_msg, expected_len):
    """
    验证response body中任意属性的值
    :param expected_len:
    :param body:
    :param body_msg:
    :return:
    """
    try:
        data = body[body_msg]
        assert len(data) >= expected_len
        return True
    except:
        logs.get_log('assert.log').error("Response body len")
        Consts.RESULT_LIST.append('fail')
        raise
    pass


if __name__ == '__main__':
    # 示例
    body1 = {'q': 1, 'w': '2', 'e': 3}
    assert_code(200, 200)
    assert_body(body1, 'q', 1)
    assert_in_text(body1, 'q')
    assert_text(body1['q'], 1)
    assert_time(1, 2)
    assert_len(body1, 'w', 1)