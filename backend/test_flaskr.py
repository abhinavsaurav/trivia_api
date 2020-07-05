import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres','password','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    
    # Unit test requires method to begin with test word to test the functions
    
    def test_get_categories(self):
        ''' Test Case to retrieve categories function '''
        
        response=self.client().get('/categories')
        data=json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['categories'])
    
    def test_get_paginate_questions(self):
        ''' Test case to get questions as paginated data '''
        response=self.client().get('/questions?page=1')
        data=json.loads(response.data)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['questions']))
    
    def test_404_get_paginate_questions(self):
        response=self.client().get('/questions?page=1000')
        data=json.loads(response.data)
        
        self.assertEqual(response.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['Message'],"Not Found")
        
    def test_delete_question(self):
        response=self.client().delete('/questions/5')
        data=json.loads(response.data)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        
    def test_404_delete_question(self):
        response=self.client().delete('/questions/1000')
        data=json.loads(response.data)
        
        self.assertEqual(response.status_code,404)
        self.assertTrue(data['Message'])
        
    def test_add_questions(self):
        test_data={
            "question":"Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?",
            "answer":"Maya Angelou",
            "category":'2',
            "difficulty":4
        }
        response=self.client().post('/questions',json=test_data) #9 and 5 missing add it
        data=json.loads(response.data)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True) 
    
    def test_422_add_questions(self):
        test_data={
            "answer":"Maya Angelou",
            "category":'2',
            "difficulty":4
        }
        response=self.client().post('/questions',json=test_data) #9 and 5 missing add it
        data=json.loads(response.data)
        
        self.assertEqual(response.status_code,422)
        self.assertEqual(data['success'],False)
    
    def test_search_question(self):
        test_data={
            "searchTerm":"Tom"
        }
        response=self.client().post('/questionsSearch',json=test_data)
        data=json.loads(response.data)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])

    def test_404_search_question(self):
        test_data={
            "searchTerm":"jager"
        }
        response=self.client().post('/questionsSearch',json=test_data)
        data=json.loads(response.data)
        
        self.assertEqual(response.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertTrue(data['Message'])
    
    def test_question_by_category(self):
        response=self.client().get('/categories/1/questions')
        data=json.loads(response.data)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        
    def test_405_question_by_category(self):
        response=self.client().get('/categories/1000/questions')
        data=json.loads(response.data)
        
        self.assertEqual(response.status_code,405)
        self.assertEqual(data['success'],False)
        self.assertTrue(data['Message'])
        
    def test_quiz(self):
        test_data={  
            'previous_questions': [],
            'quiz_category': {
                'type': 'Science',
                'id': 1
            }
        }
        response=self.client().post('/quizzes',json=test_data)
        data=json.loads(response.data)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        
    def test_422_quiz(self):
        test_data={
            'previous_questions': [],
            'quiz_category': {
                'type': 'Science'
            }
        }
        response=self.client().post('/quizzes',json=test_data)
        data=json.loads(response.data)
        
        self.assertEqual(response.status_code,422)
        self.assertEqual(data['success'],False)
    
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()