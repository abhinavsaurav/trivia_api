import os
import sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  # db=SQLAlchemy()
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors=CORS(app,resource={r"/api/*":{"origins":"*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods','GET, POST, PATCH, DELETE, OPTIONS')    
    return response
  
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories',methods=['GET'])
  def get_categories():
    categories= Category.query.all()
    formatted_categ = {category.id:category.type for category in categories}
    return jsonify({
      "success":True,
      "categories":formatted_categ})

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions',methods=['GET'])
  def paginate_questions():
    questions= Question.query.all()
    categories=Category.query.all()
    
    formatted_questions= [question.format() for question in questions]
    formatted_categories= {category.id:category.type for category in categories}
    
    page=request.args.get('page',1,type=int)
    start=(page-1)*10
    end=start+10
    
    if(len(formatted_questions[start:end])==0):
      abort(404)
    
    return jsonify({
          'success': True,
          'questions': formatted_questions[start:end],
          'total_questions': len(formatted_questions),
          'categories': formatted_categories,
          'current_category': None
      })
    
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    error=False
    try:
      question=Question.query.get(question_id)
      # imported db from models won't work if you explicitly define
      db.session.delete(question)
      db.session.commit()
    except:
      error=True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
    if error:
      abort(404)
    else:
      return jsonify({
        "success":True
      })
      
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.
  
  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  
  @app.route('/questions',methods=['POST'])
  def add_question():
    error=False
    try:
      data = request.get_json()
      print(data)
      question = Question(question=data['question'],answer=data['answer'],category=data['category'],difficulty=data['difficulty'])
      db.session.add(question)
      # question.insert()
      selection = Question.query.order_by('id').all()
      # selection2= Question.query.order_by('id').limit(1).all()
      # print(selection,"---",selection2)
      db.session.commit()
    except :
      error=True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
    
    if error:
      abort(422)
    else:
      return jsonify({
        'success':True,
      })

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questionsSearch',methods=['POST'])
  def question_by_phrase():
    
    data=request.get_json()['searchTerm']
    questions =Question.query.filter(Question.question.ilike('%{}%'.format(data))).all()
    # print("reaching here")
    if not questions:
      abort(404)
    
    formatted_quest= [ question.format() for question in questions]
    
    
    return jsonify({
      "success":True,
      "questions":formatted_quest,
      "total_questions":len(questions),
      "current_category":None
    })

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:catg_id>/questions',methods=['GET'])
  def questionByCategory(catg_id):
    # questions=db.session.query(Category,Question).join(Question,Question.category==Category.id).filter(Category.id==catg_id).all()
    # The above query will return from both the tables where as below query will join but return only from questions 
    questions=Question.query.join(Category, Question.category==Category.id).filter(Category.id==catg_id).all()
    if len(questions)==0:
      abort(405)
    formatted_quest=[question.format() for question in questions]
    return jsonify({
      "success":True,
      "questions":formatted_quest,
      "total_questions":len(questions),
      "current_category":None
    })
    
  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes',methods=['POST'])
  def quiz():
    try:
      data=request.get_json()
      # print(data[''])
      questions_ids=data['previous_questions']
      quiz_catg=data['quiz_category']
      # print(question_ids,"--",quiz_catg)
      if quiz_catg['id'] is None:
        abort(422)
      
      if quiz_catg['id'] == 0:
        questions=Question.query.filter(~Question.id.in_(questions_ids)).all()
      else:
        questions=Question.query.join(Category,Category.id==Question.category).filter(~Question.id.in_(questions_ids),Category.id == quiz_catg['id']).all()
      formatted_quest=[]
      randomQuestionData=[]
      if questions:
        formatted_quest=[question.format() for question in questions]
        randomQuestionData=random.choice(formatted_quest)
      
      
      if not questions:
        return jsonify({
          "success":True,
          "questions":False
        })
      else:
        return jsonify({
            "success":True,
            "previous_questions":data['previous_questions'],
            "question": randomQuestionData
        })
    except :
      abort(422)
    
   
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success":False,
      "error":400,
      "Message":"Bad Request"
    }), 400
  
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success":False,
      "error":404,
      "Message":"Not Found"
    }), 404
    
  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success":False,
      "error":405,
      "Message":"Method is Not allowed for requested URL"
    }) , 405
  
  @app.errorhandler(422)
  def unprocessable_entity(error):
    return jsonify({
      "success":False,
      "error":422,
      "Message":"Unprocessable entity"
    }), 422
    
  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      "success":False,
      "error":500,
      "Message":"Server Error"
    }), 500
  
  
  return app

    