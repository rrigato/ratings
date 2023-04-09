import unittest

class TestRatingsEntityModel(unittest.TestCase):

    def test_television_rating_bad_input_str_attributes(self):
        """TelevisionRating str attributes passed invalid input raises TypeError"""
        from ratings.entities.ratings_entities import TelevisionRating

        mock_invalid_types = [
            set(["a", "b"]),
            3005,
            11.29,
            (1, 2, 3),
            {},
            ["a", "list"]
        ]

        for mock_invalid_type in mock_invalid_types:
            with self.subTest(mock_invalid_type=mock_invalid_type):

                mock_television_rating = TelevisionRating()
                
                with self.assertRaises(TypeError):
                    mock_television_rating.time_slot = mock_invalid_type

                with self.assertRaises(TypeError):
                    mock_television_rating.show_name = mock_invalid_type


    def test_television_rating_bad_input_numeric_attributes(self):
        """TelevisionRating numeric attributes passed invalid input raises TypeError"""
        from ratings.entities.ratings_entities import TelevisionRating

        mock_invalid_types = [
            set(["a", "b"]),
            "3005",
            "11.29",
            (1, 2, 3),
            {},
            ["a", "list"]
        ]

        for mock_invalid_type in mock_invalid_types:
            with self.subTest(mock_invalid_type=mock_invalid_type):

                mock_television_rating = TelevisionRating()

                with self.assertRaises(TypeError):
                    mock_television_rating.rating = mock_invalid_type
                
                with self.assertRaises(TypeError):
                    mock_television_rating.rating_18_49 = mock_invalid_type

                with self.assertRaises(TypeError):
                    mock_television_rating.household = mock_invalid_type

                with self.assertRaises(TypeError):
                    mock_television_rating.household_18_49 = mock_invalid_type


    

    def test_television_ratings_matches_fixture(self):
        """Each attribute in fixutre is a property for the entity"""
        from fixtures.ratings_fixtures import get_mock_television_ratings
        from ratings.entities.ratings_entities import TelevisionRating


        fixture_television_rating_attributes = [
            attribute_name for attribute_name 
            in dir(get_mock_television_ratings(1)[0]) 
            if not attribute_name.startswith("_")
        ]
        
        television_rating_attributes = [
            attribute_name for attribute_name 
            in dir(TelevisionRating) 
            if not attribute_name.startswith("_")
        ]
        
        self.assertEqual(
            len(fixture_television_rating_attributes),
            len(television_rating_attributes),
            msg="""\n
                Every fixture attribute might not have a corresponding
                property for TelevisionRating entity
            """
            )

        for fixture_attr in fixture_television_rating_attributes:
            self.assertIn(
                fixture_attr,
                television_rating_attributes
            )


    def test_secret_config(self):
        """invalid datatypes for entity raise TypeError"""
        from ratings.entities.ratings_entities import SecretConfig

        mock_invalid_types = [
            set(["a", "b"]),
            3005,
            11.29,
            (1, 2, 3),
            {},
            ["a", "list"]
        ]

        object_properties = [
            attr_name for attr_name in dir(SecretConfig())
            if not attr_name.startswith("_")
        ]
        for mock_invalid_type in mock_invalid_types:
            with self.subTest(mock_invalid_type=mock_invalid_type):

                mock_entity = SecretConfig()
                
                
                
                for object_property in object_properties:
                    with self.assertRaises(TypeError):
                        setattr(
                            mock_entity, 
                            object_property,
                            mock_invalid_type
                        )

