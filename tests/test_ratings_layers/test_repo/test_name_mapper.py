import unittest

class TestNameMapper(unittest.TestCase):
    def test_get_table_column_name_mapping(self):
        """Each column name mapping value for a ratings post is a str"""
        from ratings_layers.repo.name_mapper import get_table_column_name_mapping
        
        self.assertGreater(
            len(get_table_column_name_mapping().keys()),
            10
        )
        for column_name in get_table_column_name_mapping().keys():
            self.assertEqual(
                type(get_table_column_name_mapping()[column_name]),
                str
            )

    @unittest.skip("skipping for now")
    def test_get_table_column_name_mapping_viewers_e2e(self):
        """Bug where viewers key was not mapped"""
        from ratings_layers.repo.name_mapper import get_table_column_name_mapping

        self.assertEqual(
            type(get_table_column_name_mapping()["viewers"]),
            str
        )      
        