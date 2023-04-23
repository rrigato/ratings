import unittest

class TestNameMapper(unittest.TestCase):
    def test_get_table_column_name_mapping(self):
        """Each column name mapping value for a ratings post is a str"""
        from ratings.repo.name_mapper import get_table_column_name_mapping
        
        self.assertGreater(
            len(get_table_column_name_mapping().keys()),
            10
        )
        for column_name in get_table_column_name_mapping().keys():
            self.assertEqual(
                type(get_table_column_name_mapping()[column_name]),
                str
            )
    
    def test_table_column_to_television_rating(self):
        """map table column name to TelevisionRating entity"""
        from ratings.repo.name_mapper import get_table_column_name_mapping
        from ratings.repo.name_mapper import table_column_to_television_rating
        

        self.assertEqual(
            len(set(get_table_column_name_mapping().values())) - 1,
            len(table_column_to_television_rating().keys()),
            msg="\n\n TODO - map is_rerun"
        )
        

    def test_get_table_column_name_mapping_viewers_e2e(self):
        """Bug where viewers key was not mapped"""
        from ratings.repo.name_mapper import get_table_column_name_mapping

        self.assertEqual(
            type(get_table_column_name_mapping()["viewers"]),
            str
        )      


    def test_get_table_column_name_mapping_18_49(self):
        """Bug where 18-49 key was not mapped"""
        from ratings.repo.name_mapper import get_table_column_name_mapping

        self.assertEqual(
            type(get_table_column_name_mapping()["18-49"]),
            str
        )    


    def test_get_table_column_name_mapping_timeslot(self):
        """Bug where timeslot is not mapped"""
        from ratings.repo.name_mapper import get_table_column_name_mapping

        self.assertEqual(
            type(get_table_column_name_mapping()["timeslot"]),
            str
        )    


    def test_get_table_column_name_mapping_rating(self):
        """Bug where rating is not mapped"""
        from ratings.repo.name_mapper import get_table_column_name_mapping

        self.assertEqual(
            type(get_table_column_name_mapping()["rating"]),
            str
        )    


    def test_keys_to_ignore(self):
        """Each column name mapping value for a ratings post is a str"""
        from ratings.repo.name_mapper import keys_to_ignore
        
        self.assertGreater(
            len(keys_to_ignore()),
            0
        )
        for key_name in keys_to_ignore():
            self.assertIsInstance(
                key_name,
                str
            )
