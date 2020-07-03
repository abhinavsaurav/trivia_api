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
    # {category.id:category.type for category in categories}
    # print(formatted_categ)
    # categ_dict={}
    # for diction in formatted_categ:
    #   categ_dict[diction['id']]=diction['type']
    
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
    # print("line1")
    data=request.get_json()['searchTerm']
    # print("printing this",data)
    
    questions =Question.query.filter(Question.question.ilike('%{}%'.format(data))).all()
    # print("reaching here")
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
    try:
      # questions=db.session.query(Category,Question).join(Question,Question.category==Category.id).filter(Category.id==catg_id).all()
      # The above query will return from both the tables where as below query will join but return only from questions 
      questions=Question.query.join(Category, Question.category==Category.id).filter(Category.id==catg_id).all()
      formatted_quest=[question.format() for question in questions]
      return jsonify({
        "success":True,
        "questions":formatted_quest,
        "total_questions":len(questions),
        "current_category":None
      })
    except :
      abort(404)

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
      question_ids=data['previous_questions']
      quiz_catg=data['quiz_category']
      print(question_ids,"--",quiz_catg)
      if quiz_catg['id'] == 0:
        questions=Question.query.all()
      else:
        questions=Question.query.join(Category,Category.id==Question.category).filter(~Question.id.in_(question_ids),Category.id == quiz_catg['id']).all()
      # if not quiz_catg:
      #   abort(422)
      
      print(questions)
      returned_ids=[]
      randomQuestionData=[]
      found=False
      if questions:
        returned_ids=[question.id for question in questions]
        print(returned_ids)
      if returned_ids:
        randomQuestionId=random.choice(returned_ids)
        for question in questions:
          if question.id==randomQuestionId:
            randomQuestionData.append(question.format())
            found=True
            break
      
      if not found:
        return jsonify({
          "success":True,
          "questions":None
        }) ,404
      else:
        return jsonify({
            "success":True,
            "previous_questions":data['previous_questions'],
            "question": randomQuestionData
        })
    except :
      abort(422)
    
    #   try:
  #     data = request.get_json()
  #     # check given category
  #     category_id = int(data["quiz_category"])
  #     category = Category.query.get(category_id)
  #     previous_questions = data["previous_questions"]
  #     if not category == None:  
  #       if "previous_questions" in data and len(previous_questions) > 0:
  #         questions = Question.query.filter(
  #           Question.id.notin_(previous_questions),
  #           Question.category == category.id
  #           ).all()  
  #       else:
  #         questions = Question.query.filter(Question.category == category.id).all()
  #     else:
  #       if "previous_questions" in data and len(previous_questions) > 0:
  #         questions = Question.query.filter(Question.id.notin_(previous_questions)).all()  
  #       else:
  #         questions = Question.query.all()
  #     max = len(questions) - 1
  #     if max > 0:
  #       question = questions[random.randint(0, max)].format()
  #     else:
  #       question = False
  #     return jsonify({
  #       "success": True,
  #       "question": question
  #     })
  #   except:
  #     abort(500, "An error occured while trying to load the next question")
    
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  return app

    