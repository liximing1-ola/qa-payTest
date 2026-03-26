# -*- coding: utf-8 -*-
"""
HTML测试报告生成器

基于unittest的HTML测试报告生成工具，支持图表展示
"""
import datetime
import sys
import io
import unittest
from xml.sax import saxutils


# 状态码映射
STATUS_MAP = {0: '通过', 1: '失败', 2: '错误'}


class OutputRedirector:
    """输出重定向包装器"""

    def __init__(self, fp):
        self.fp = fp

    def write(self, s):
        self.fp.write(s)

    def writelines(self, lines):
        self.fp.writelines(lines)

    def flush(self):
        self.fp.flush()


stdout_redirector = OutputRedirector(sys.stdout)
stderr_redirector = OutputRedirector(sys.stderr)


class TemplateMixin:
    """HTML模板混合类"""

    DEFAULT_TITLE = 'Unit Test Report'
    DEFAULT_DESCRIPTION = ''

    # HTML主模板
    HTML_TMPL = r"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>%(title)s</title>
    <meta name="generator" content="%(generator)s"/>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <link href="http://cdn.bootcss.com/bootstrap/3.3.0/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.bootcss.com/echarts/3.8.5/echarts.common.min.js"></script>
    %(stylesheet)s
</head>
<body>
    <script language="javascript" type="text/javascript">
    output_list = Array();
    function showCase(level) {
        trs = document.getElementsByTagName("tr");
        for (var i = 0; i < trs.length; i++) {
            tr = trs[i];
            id = tr.id;
            if (id.substr(0,2) == 'ft') {
                tr.className = level < 1 ? 'hiddenRow' : '';
            }
            if (id.substr(0,2) == 'pt') {
                tr.className = level > 1 ? '' : 'hiddenRow';
            }
        }
    }
    function showClassDetail(cid, count) {
        var id_list = Array(count);
        var toHide = 1;
        for (var i = 0; i < count; i++) {
            tid0 = 't' + cid.substr(1) + '.' + (i+1);
            tid = 'f' + tid0;
            tr = document.getElementById(tid);
            if (!tr) {
                tid = 'p' + tid0;
                tr = document.getElementById(tid);
            }
            id_list[i] = tid;
            if (tr.className) toHide = 0;
        }
        for (var i = 0; i < count; i++) {
            tid = id_list[i];
            if (toHide) {
                document.getElementById('div_'+tid).style.display = 'none';
                document.getElementById(tid).className = 'hiddenRow';
            } else {
                document.getElementById(tid).className = '';
            }
        }
    }
    function showTestDetail(div_id){
        var details_div = document.getElementById(div_id);
        var displayState = details_div.style.display;
        details_div.style.display = displayState != 'block' ? 'block' : 'none';
    }
    function html_escape(s) {
        return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    }
    </script>
    <div id="div_base">
        %(heading)s
        %(report)s
        %(ending)s
        %(chart_script)s
    </div>
</body>
</html>"""

    # ECharts图表脚本
    ECHARTS_SCRIPT = """
    <script type="text/javascript">
        var myChart = echarts.init(document.getElementById('chart'));
        var option = {
            title: {text: '测试执行情况', x:'center'},
            tooltip: {trigger: 'item', formatter: "{a} <br/>{b} : {c} ({d}%%)"},
            color: ['#95b75d', 'grey', '#b64645'],
            legend: {orient: 'vertical', left: 'left', data: ['通过','失败','错误']},
            series: [{
                name: '测试执行情况',
                type: 'pie',
                radius: '60%%',
                center: ['50%%', '60%%'],
                data:[
                    {value:%(Pass)s, name:'通过'},
                    {value:%(fail)s, name:'失败'},
                    {value:%(error)s, name:'错误'}
                ],
                itemStyle: {emphasis: {shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)'}}
            }]
        };
        myChart.setOption(option);
    </script>
    """

    # 样式表模板
    STYLESHEET_TMPL = """
<style type="text/css" media="screen">
    body { font-family: Microsoft YaHei,Consolas,arial,sans-serif; font-size: 80%; }
    table { font-size: 100%; }
    pre { white-space: pre-wrap; word-wrap: break-word; }
    h1 { font-size: 16pt; color: gray; }
    .heading { margin-top: 0ex; margin-bottom: 1ex; }
    .heading .attribute { margin-top: 1ex; margin-bottom: 0; }
    .heading .description { margin-top: 2ex; margin-bottom: 3ex; }
    .popup_window { display: none; position: relative; left: 0px; top: 0px; padding: 10px;
                    font-family: "Lucida Console", "Courier New", Courier, monospace;
                    text-align: left; font-size: 8pt; }
    #show_detail_line { margin-top: 3ex; margin-bottom: 1ex; }
    #result_table { width: 99%; }
    #header_row { font-weight: bold; color: #303641; background-color: #ebebeb; }
    #total_row { font-weight: bold; }
    .passClass { background-color: #bdedbc; }
    .failClass { background-color: #ffefa4; }
    .errorClass { background-color: #ffc9c9; }
    .passCase { color: #6c6; }
    .failCase { color: #FF6600; font-weight: bold; }
    .errorCase { color: #c00; font-weight: bold; }
    .hiddenRow { display: none; }
    .testcase { margin-left: 2em; }
    #div_base { position:absolute; top:0%%; left:5%%; right:5%%; width: auto; height: auto; margin: -15px 0 0 0; }
</style>
"""

    # 标题模板
    HEADING_TMPL = """
    <div class='page-header'>
        <h1>%(title)s</h1>
        %(parameters)s
    </div>
    <div style="float: left;width:50%%;"><p class='description'>%(description)s</p></div>
    <div id="chart" style="width:50%%;height:400px;float:left;"></div>
"""

    HEADING_ATTRIBUTE_TMPL = """<p class='attribute'><strong>%(name)s:</strong> %(value)s</p>"""

    # 报告模板
    REPORT_TMPL = """
    <div class="btn-group btn-group-sm">
        <button class="btn btn-default" onclick='javascript:showCase(0)'>总结</button>
        <button class="btn btn-default" onclick='javascript:showCase(1)'>失败</button>
        <button class="btn btn-default" onclick='javascript:showCase(2)'>全部</button>
    </div>
    <p></p>
    <table id='result_table' class="table table-bordered">
        <colgroup>
            <col align='left' />
            <col align='right' />
            <col align='right' />
            <col align='right' />
            <col align='right' />
            <col align='right' />
        </colgroup>
        <tr id='header_row'>
            <td>测试套件/测试用例</td>
            <td>总数</td>
            <td>通过</td>
            <td>失败</td>
            <td>错误</td>
            <td>查看</td>
        </tr>
        %(test_list)s
        <tr id='total_row'>
            <td>总计</td>
            <td>%(count)s</td>
            <td>%(Pass)s</td>
            <td>%(fail)s</td>
            <td>%(error)s</td>
            <td>&nbsp;</td>
        </tr>
    </table>
"""

    REPORT_CLASS_TMPL = """
    <tr class='%(style)s'>
        <td>%(desc)s</td>
        <td>%(count)s</td>
        <td>%(Pass)s</td>
        <td>%(fail)s</td>
        <td>%(error)s</td>
        <td><a href="javascript:showClassDetail('%(cid)s',%(count)s)">详情</a></td>
    </tr>
"""

    REPORT_TEST_WITH_OUTPUT_TMPL = """
<tr id='%(tid)s' class='%(Class)s'>
    <td class='%(style)s'><div class='testcase'>%(desc)s</div></td>
    <td colspan='5' align='center'>
    <a class="popup_link" onfocus='this.blur();' href="javascript:showTestDetail('div_%(tid)s')">%(status)s</a>
    <div id='div_%(tid)s' class="popup_window"><pre>%(script)s</pre></div>
    </td>
</tr>
"""

    REPORT_TEST_NO_OUTPUT_TMPL = """
<tr id='%(tid)s' class='%(Class)s'>
    <td class='%(style)s'><div class='testcase'>%(desc)s</div></td>
    <td colspan='5' align='center'>%(status)s</td>
</tr>
"""

    REPORT_TEST_OUTPUT_TMPL = """%(id)s: %(output)s"""

    ENDING_TMPL = """<div id='ending'>&nbsp;</div>"""


class TestResult(unittest.TestResult):
    """测试结果收集器"""

    def __init__(self, verbosity=1):
        super().__init__()
        self.stdout0 = None
        self.stderr0 = None
        self.success_count = 0
        self.failure_count = 0
        self.error_count = 0
        self.verbosity = verbosity
        self.result = []
        self.subtestlist = []

    def startTest(self, test):
        super().startTest(test)
        self.outputBuffer = io.StringIO()
        stdout_redirector.fp = self.outputBuffer
        stderr_redirector.fp = self.outputBuffer
        self.stdout0 = sys.stdout
        self.stderr0 = sys.stderr
        sys.stdout = stdout_redirector
        sys.stderr = stderr_redirector

    def complete_output(self):
        """断开输出重定向并返回缓冲区内容"""
        if self.stdout0:
            sys.stdout = self.stdout0
            sys.stderr = self.stderr0
            self.stdout0 = None
            self.stderr0 = None
        return self.outputBuffer.getvalue()

    def stopTest(self, test):
        self.complete_output()

    def addSuccess(self, test):
        if test not in self.subtestlist:
            self.success_count += 1
            super().addSuccess(test)
            output = self.complete_output()
            self.result.append((0, test, output, ''))
            self._write_progress('ok ' if self.verbosity > 1 else '.', test)

    def addError(self, test, err):
        self.error_count += 1
        super().addError(self, test, err)
        _, _exc_str = self.errors[-1]
        output = self.complete_output()
        self.result.append((2, test, output, _exc_str))
        self._write_progress('E  ' if self.verbosity > 1 else 'E', test)

    def addFailure(self, test, err):
        self.failure_count += 1
        super().addFailure(self, test, err)
        _, _exc_str = self.failures[-1]
        output = self.complete_output()
        self.result.append((1, test, output, _exc_str))
        self._write_progress('F  ' if self.verbosity > 1 else 'F', test)

    def _write_progress(self, marker, test):
        """写入进度标记"""
        sys.stderr.write(marker)
        if self.verbosity > 1:
            sys.stderr.write(str(test))
        sys.stderr.write('\n')

    def addSubTest(self, test, subtest, err):
        if err is not None:
            if getattr(self, 'failfast', False):
                self.stop()
            if issubclass(err[0], test.failureException):
                self._add_sub_failure(test, subtest, err)
            else:
                self._add_sub_error(test, subtest, err)
            self._mirrorOutput = True
        else:
            self._add_sub_success(test, subtest)

    def _add_sub_failure(self, test, subtest, err):
        self.failure_count += 1
        self.failures.append((subtest, self._exc_info_to_string(err, subtest)))
        output = self.complete_output()
        self.result.append((1, test, output + '\nSubTestCase Failed:\n' + str(subtest),
                            self._exc_info_to_string(err, subtest)))
        self._write_progress('F  ' if self.verbosity > 1 else 'F', subtest)

    def _add_sub_error(self, test, subtest, err):
        self.error_count += 1
        self.errors.append((subtest, self._exc_info_to_string(err, subtest)))
        output = self.complete_output()
        self.result.append((2, test, output + '\nSubTestCase Error:\n' + str(subtest),
                            self._exc_info_to_string(err, subtest)))
        self._write_progress('E  ' if self.verbosity > 1 else 'E', subtest)

    def _add_sub_success(self, test, subtest):
        self.subtestlist.append(subtest)
        self.subtestlist.append(test)
        self.success_count += 1
        output = self.complete_output()
        self.result.append((0, test, output + '\nSubTestCase Pass:\n' + str(subtest), ''))
        self._write_progress('ok ' if self.verbosity > 1 else '.', subtest)


class HTMLTestRunner(TemplateMixin):
    """HTML测试报告运行器"""

    def __init__(self, stream=sys.stdout, verbosity=1, title=None, description=None):
        self.stream = stream
        self.verbosity = verbosity
        self.title = title or self.DEFAULT_TITLE
        self.description = description or self.DEFAULT_DESCRIPTION
        self.startTime = datetime.datetime.now()

    def run(self, test):
        """运行测试并生成报告"""
        result = TestResult(self.verbosity)
        test(result)
        self.stopTime = datetime.datetime.now()
        self.generateReport(test, result)
        print(f'\nTime Elapsed: {self.stopTime - self.startTime}', file=sys.stderr)
        return result

    def sortResult(self, result_list):
        """按类对结果进行分组"""
        class_map = {}
        classes = []
        for n, t, o, e in result_list:
            cls = t.__class__
            if cls not in class_map:
                class_map[cls] = []
                classes.append(cls)
            class_map[cls].append((n, t, o, e))
        return [(cls, class_map[cls]) for cls in classes]

    def getReportAttributes(self, result):
        """获取报告属性列表"""
        start_time = str(self.startTime)[:19]
        duration = str(self.stopTime - self.startTime)
        status_parts = []
        if result.success_count:
            status_parts.append(f'通过 {result.success_count}')
        if result.failure_count:
            status_parts.append(f'失败 {result.failure_count}')
        if result.error_count:
            status_parts.append(f'错误 {result.error_count}')
        status = ' '.join(status_parts) if status_parts else 'none'
        return [('开始时间', start_time), ('运行时长', duration), ('状态', status)]

    def generateReport(self, test, result):
        """生成HTML报告"""
        report_attrs = self.getReportAttributes(result)
        output = self.HTML_TMPL % dict(
            title=saxutils.escape(self.title),
            generator='HTMLTestRunner',
            stylesheet=self._generate_stylesheet(),
            heading=self._generate_heading(report_attrs),
            report=self._generate_report(result),
            ending=self._generate_ending(),
            chart_script=self._generate_chart(result)
        )
        # self.stream.write(output)

    def _generate_stylesheet(self):
        return self.STYLESHEET_TMPL

    def _generate_heading(self, report_attrs):
        a_lines = []
        for name, value in report_attrs:
            line = self.HEADING_ATTRIBUTE_TMPL % dict(
                name=saxutils.escape(name),
                value=saxutils.escape(value),
            )
            a_lines.append(line)
        return self.HEADING_TMPL % dict(
            title=saxutils.escape(self.title),
            parameters=''.join(a_lines),
            description=saxutils.escape(self.description),
        )

    def _generate_report(self, result):
        rows = []
        sorted_result = self.sortResult(result.result)
        for cid, (cls, cls_results) in enumerate(sorted_result):
            np = nf = ne = 0
            for n, t, o, e in cls_results:
                if n == 0:
                    np += 1
                elif n == 1:
                    nf += 1
                else:
                    ne += 1

            name = cls.__name__ if cls.__module__ == "__main__" else f"{cls.__module__}.{cls.__name__}"
            doc = cls.__doc__.split("\n")[0] if cls.__doc__ else ""
            desc = f"{name}: {doc}" if doc else name

            row = self.REPORT_CLASS_TMPL % dict(
                style='errorClass' if ne > 0 else ('failClass' if nf > 0 else 'passClass'),
                desc=desc,
                count=np + nf + ne,
                Pass=np,
                fail=nf,
                error=ne,
                cid=f'c{cid + 1}',
            )
            rows.append(row)

            for tid, (n, t, o, e) in enumerate(cls_results):
                self._generate_report_test(rows, cid, tid, n, t, o, e)

        return self.REPORT_TMPL % dict(
            test_list=''.join(rows),
            count=str(result.success_count + result.failure_count + result.error_count),
            Pass=str(result.success_count),
            fail=str(result.failure_count),
            error=str(result.error_count),
        )

    def _generate_chart(self, result):
        return self.ECHARTS_SCRIPT % dict(
            Pass=str(result.success_count),
            fail=str(result.failure_count),
            error=str(result.error_count),
        )

    def _generate_report_test(self, rows, cid, tid, n, t, o, e):
        has_output = bool(o or e)
        tid = ('p' if n == 0 else 'f') + f't{cid + 1}.{tid + 1}'
        name = t.id().split('.')[-1]
        doc = t.shortDescription() or ""
        desc = f"{name}: {doc}" if doc else name
        tmpl = self.REPORT_TEST_WITH_OUTPUT_TMPL if has_output else self.REPORT_TEST_NO_OUTPUT_TMPL

        script = self.REPORT_TEST_OUTPUT_TMPL % dict(id=tid, output=saxutils.escape(o + e))

        row = tmpl % dict(
            tid=tid,
            Class='hiddenRow' if n == 0 else 'none',
            style='errorCase' if n == 2 else ('failCase' if n == 1 else 'none'),
            desc=desc,
            script=script,
            status=STATUS_MAP[n],
        )
        rows.append(row)

    def _generate_ending(self):
        return self.ENDING_TMPL


class TestProgram(unittest.TestProgram):
    """测试程序入口"""

    def runTests(self):
        if self.testRunner is None:
            self.testRunner = HTMLTestRunner(verbosity=self.verbosity)
        super().runTests()


main = TestProgram

if __name__ == "__main__":
    main(module=None)
