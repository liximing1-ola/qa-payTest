"""
封装assert方法
"""
import json
from Common import consts


def assert_code(code, expected_code, reason):
    """
    验证response状态码
    :param reason: 上报错误信息
    :param code: 实际结果
    :param expected_code: 预期结果
    :return:
    """
    try:
        assert code == expected_code
        return True
    except:
        consts.fail_case_reason.append(reason)
        raise


def assert_body(body, body_msg, expected_msg, reason):
    """
    验证response body中任意属性的值
    :param reason: 上报错误信息
    :param body: 返回信息体
    :param body_msg:
    :param expected_msg:
    :return:
    """
    try:
        msg = body[body_msg]
        assert msg == expected_msg
        return True
    except:
        consts.fail_case_reason.append(reason)
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
        consts.fail_case_reason.append('fail')
        raise

def assert_len(body, body_msg, expected_len, reason):
    """
    验证response body中任意属性的值
    :param reason:
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
        consts.fail_case_reason.append(reason)
        raise

def assert_equal(actual_result, expect_result, reason):
    try:
        assert actual_result == expect_result
        return True
    except:
        consts.fail_case_reason.append(reason)
        print('实际结果： {}'.format(actual_result))
        raise


if __name__ == '__main__':
    # 示例
    res = {'code': 200, 'body': {'success': False, 'msg': '余额不足，无法支付'}, 'time_consuming': 9.316, 'time_total': 0.009316}
    assert_code(res['code'], 300, res['body'])