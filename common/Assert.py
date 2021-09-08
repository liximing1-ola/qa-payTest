"""
封装assert方法
"""
import json
from common import Consts

def assert_code(actual_code, expected_code):
    """
    验证response状态码
    :param actual_code: 实际结果
    :param expected_code: 预期结果
    """
    try:
        assert actual_code == expected_code
        return True
    except:
        reason = '实际Code: {}, 预期Code: {}, 对比结果不一致，fail，望严查!'.format(actual_code, expected_code)
        Consts.fail_case_reason.append(reason)
        raise

def assert_body(body, body_msg, expected_msg, reason):
    """
    验证response状态码
    :param body: 返回值
    :param body_msg: 参数
    :param expected_msg: 预期结果
    :param reason: 原因
    """
    try:
        msg = body[body_msg]
        assert msg == expected_msg
        return True
    except:
        Consts.fail_case_reason.append(reason)
        raise

def assert_len(actual_len, expect_len):
    """
    :param actual_len: 实际结果
    :param expect_len: 预期结果
    """
    try:
        assert actual_len >= expect_len
        return True
    except:
        reason = '实际结果: {}, 预期结果: {}, 对比结果不一致，用例执行失败，望严查!'.format(actual_len, expect_len)
        Consts.fail_case_reason.append(reason)
        raise

def assert_equal(actual_result, expect_result):
    """
    :param actual_result: 实际结果
    :param expect_result: 预期结果
    """
    try:
        assert actual_result == expect_result
        return True
    except:
        reason = '实际结果: {}, 预期结果: {}, 对比结果不一致，用例执行失败，望严查!'.format(actual_result, expect_result)
        Consts.fail_case_reason.append(reason)
        raise

def assert_in_text(body, expected_msg):
    """
    :param body: 返回值
    :param expected_msg: 预期结果
    """
    try:
        text = json.dumps(body, ensure_ascii=False)
        assert expected_msg in text
        return True
    except:
        Consts.fail_case_reason.append('fail')
        raise


if __name__ == '__main__':
    # 示例
    res = {'code': 200, 'body': {'success': False, 'msg': '余额不足，无法支付'},
           'time_consuming': 9.316, 'time_total': 0.009316}
    assert_code(res['code'], 300)