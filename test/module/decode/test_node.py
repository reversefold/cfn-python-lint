"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import six
import cfnlint.decode.node  # pylint: disable=E0401
from testlib.testcase import BaseTestCase


class TestNode(BaseTestCase):
    """Test Node Objects """

    def test_success_init(self):
        """Test Dict Object"""
        template = cfnlint.decode.node.dict_node({
            "test": "string"
        }, (0, 1), (2, 3))

        self.assertEqual(template, {"test": "string"})
        self.assertEqual(template.start_mark[0], 0)
        self.assertEqual(template.start_mark[1], 1)
        self.assertEqual(template.end_mark[0], 2)
        self.assertEqual(template.end_mark[1], 3)

    def test_success_fnif_object(self):
        """Test Dict Object"""
        template = cfnlint.decode.node.dict_node({
            "Fn::If": [
                "string",
                cfnlint.decode.node.dict_node({"Test": True}, (0, 1), (2, 3)),
                cfnlint.decode.node.dict_node({"Test": False}, (0, 1), (2, 3))]
        }, (0, 1), (2, 3))

        results = []
        for items, p in template.items_safe():
            results.append((items, p))

        self.assertEqual(results, [
            ({'Test': True}, ['Fn::If', 1]),
            ({'Test': False}, ['Fn::If', 2])
        ])

    def test_success_fnif_string(self):
        """Test Dict Object"""
        template = cfnlint.decode.node.dict_node({
            "Fn::If": [
                "string",
                "True",
                "False"]
        }, (0, 1), (2, 3))

        results = []
        for items, p in template.items_safe():
            results.append((items, p))

        self.assertEqual(results, [
            ('True', ['Fn::If', 1]),
            ('False', ['Fn::If', 2])
        ])

    def test_success_fnif_list(self):
        """Test List Object"""
        template = cfnlint.decode.node.dict_node({
            "Fn::If": [
                "string",
                ["1", "2", "3"],
                ["a", "b", "c"]]
        }, (0, 1), (2, 3))

        results = []
        for items, p in template.items_safe():
            results.append((items, p))

        self.assertEqual(results, [
            (['1', '2', '3'], ['Fn::If', 1]),
            (['a', 'b', 'c'], ['Fn::If', 2])
        ])

    def test_success_fnif_ref_novalue(self):
        """Test List Object"""
        template = cfnlint.decode.node.dict_node({
            "Fn::If": [
                "string",
                True,
                cfnlint.decode.node.dict_node({
                    "Ref": "AWS::NoValue"
                }, (0, 1), (2, 3))
            ]
        }, (0, 1), (2, 3))

        results = []
        for items, p in template.items_safe():
            results.append((items, p))

        self.assertEqual(results, [(True, ['Fn::If', 1])])

    def test_success_fnif_nested(self):
        """Test List Object"""
        template = cfnlint.decode.node.dict_node({
            "Fn::If": [
                "string",
                cfnlint.decode.node.dict_node({"Test": "True"}, (0, 1), (2, 3)),
                cfnlint.decode.node.dict_node({
                    "Fn::If": [
                        "nested",
                        cfnlint.decode.node.dict_node({"NestedTest": "False,True"}, (0, 1), (2, 3)),
                        False
                    ]
                }, (0, 1), (2, 3))
            ]
        }, (0, 1), (2, 3))

        results = []
        for items, p in template.items_safe(path=['Start']):
            results.append((items, p))

        # Adding testing of Paths to make sure nested paths are good
        self.assertEqual(results, [
            ({'Test': 'True'}, ['Start', 'Fn::If', 1]),
            ({'NestedTest': 'False,True'}, ['Start', 'Fn::If', 2, 'Fn::If', 1]),
            (False, ['Start', 'Fn::If', 2, 'Fn::If', 2])
        ])

        # Testing the filters based on type
        results = []
        for items, p in template.items_safe(type_t=(dict)):
            results.append((items, p))

        self.assertEqual(results, [
            ({'Test': 'True'}, ['Fn::If', 1]),
            ({'NestedTest': 'False,True'}, ['Fn::If', 2, 'Fn::If', 1])
        ])

    def test_success_fnif_get(self):
        """Test Dict Object"""
        template = cfnlint.decode.node.dict_node({
            "Test":
                cfnlint.decode.node.dict_node({
                    "Fn::If": [
                        "string",
                        "True",
                        "False"]
                }, (0, 1), (2, 3))
        }, (0, 1), (2, 3))

        obj = template.get_safe("Test")
        self.assertEqual(obj, [('True', ['Fn::If', 1]), ('False', ['Fn::If', 2])])

    def test_success_fnif_get_nested(self):
        """Test Dict Object"""
        template = cfnlint.decode.node.dict_node({
            "Test":
                cfnlint.decode.node.dict_node({
                    "Fn::If": [
                        "string",
                        cfnlint.decode.node.dict_node({
                            "Fn::If": [
                                "string",
                                "True,True",
                                "True,False"]
                        }, (0, 1), (2, 3)),
                        "False"]
                }, (0, 1), (2, 3))
        }, (0, 1), (2, 3))

        obj = template.get_safe("Test")
        self.assertEqual(obj, [
            ('True,True', ['Fn::If', 1, 'Fn::If', 1]),
            ('True,False', ['Fn::If', 1, 'Fn::If', 2]),
            ('False', ['Fn::If', 2])
        ])

    def test_success_fnif_list_strings(self):
        """Test List Object"""
        template = cfnlint.decode.node.list_node([
            '1', '2', '3'
        ], (0, 1), (2, 3))

        results = []
        for v, p in template.items_safe():
            results.append((v, p))

        self.assertEqual(results, [('1', [0]), ('2', [1]), ('3', [2])])

    def test_success_fnif_list_conditions(self):
        """Test List Object"""
        template = cfnlint.decode.node.list_node([
            '1',
            '2',
            cfnlint.decode.node.dict_node({
                'Fn::If': [
                    'string',
                    '4',
                    '5']
            }, (0, 1), (2, 3)),
        ], (0, 1), (2, 3))

        results = []
        for v, p in template.items_safe():
            results.append((v, p))

        self.assertEqual(results, [('1', [0]), ('2', [1]), ('4', [2, 'Fn::If', 1]), ('5', [2, 'Fn::If', 2])])

    def test_success_fnif_list_conditions_no_value(self):
        """Test List Object"""
        template = cfnlint.decode.node.list_node([
            '1',
            '2',
            cfnlint.decode.node.dict_node({
                'Fn::If': [
                    'string',
                    '4',
                    cfnlint.decode.node.dict_node({
                        "Ref": "AWS::NoValue"
                    }, (0, 1), (2, 3))
                ]
            }, (0, 1), (2, 3)),
        ], (0, 1), (2, 3))

        results = []
        for v, p in template.items_safe():
            results.append((v, p))

        self.assertEqual(results, [('1', [0]), ('2', [1]), ('4', [2, 'Fn::If', 1])])

    def test_success_dict_select(self):
        """ Test if select could return an object """

        template = cfnlint.decode.node.dict_node({
            'Fn::Select': cfnlint.decode.node.list_node([
                0,
                cfnlint.decode.node.dict_node({
                    'Fn::FindInMap': ['mapping', 'key', 'value']
                }, (0, 1), (2, 3))
            ], (0, 1), (2, 3))
        }, (0, 1), (2, 3))

        self.assertTrue(template.is_function_returning_object())

    def test_failure_dict_select(self):
        """ Test if select could return an object """

        template = cfnlint.decode.node.dict_node({
            'Key': 'Value',
            'Fn::Select': cfnlint.decode.node.list_node([
                0,
                cfnlint.decode.node.dict_node({
                    'Fn::FindInMap': ['mapping', 'key', 'value']
                }, (0, 1), (2, 3))
            ], (0, 1), (2, 3))
        }, (0, 1), (2, 3))

        self.assertFalse(template.is_function_returning_object())

        template = cfnlint.decode.node.dict_node({
            'Key': 'Value',
            'Fn::Select': cfnlint.decode.node.list_node([
                0,
                cfnlint.decode.node.list_node([0, 1, 2], (0, 1), (2, 3))
            ], (0, 1), (2, 3))
        }, (0, 1), (2, 3))

        self.assertFalse(template.is_function_returning_object())
