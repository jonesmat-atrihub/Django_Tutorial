import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question


def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta( days=days )
    return Question.objects.create( question_text=question_text, pub_date=time )


class QuestionIndexViewTests( TestCase ):
    def test_no_questions(self):
        """
        If no questions, then display message
        """
        response = self.client.get( reverse( 'polls:index' ) )

        self.assertEqual( response.status_code, 200 )
        self.assertContains( response, "No polls are available." )
        self.assertQuerysetEqual( response.context['latest_question_list'], [] )

    def test_past_question(self):
        create_question( question_text="Past question.", days=-30 )
        response = self.client.get( reverse( 'polls:index' ) )

        self.assertQuerysetEqual( response.context['latest_question_list'],
                                  ['<Question: Past question.>'] )

    def test_future_question(self):
        create_question( question_text="Future question.", days=30 )
        response = self.client.get( reverse( 'polls:index' ) )
        self.assertContains( response, "No polls are available." )

        self.assertQuerysetEqual( response.context['latest_question_list'], [] )

    def test_future_and_past_questions(self):
        create_question( question_text="Future question.", days=1 )
        create_question( question_text="Past question.", days=-1 )

        response = self.client.get( reverse( 'polls:index' ) )

        self.assertQuerysetEqual( response.context['latest_question_list'],
                                  ['<Question: Past question.>'] )

    def test_two_past_questions(self):
        create_question( question_text="Past question 1.", days=-2 )
        create_question( question_text="Past question 2.", days=-1 )

        response = self.client.get( reverse( 'polls:index' ) )

        self.assertQuerysetEqual( response.context['latest_question_list'],
                                  ['<Question: Past question 2.>', '<Question: Past question 1.>'] )


class QuestionDetailViewTests( TestCase ):
    def test_future_question(self):
        future_question = create_question( question_text="Future question.", \
                                           days=5 )

        url = reverse( 'polls:detail', args=(future_question.id,) )
        response = self.client.get( url )

        self.assertEqual( response.status_code, 404 )

    def test_past_question(self):
        past_question = create_question( question_text="Past question.", days=-5 )

        url = reverse( 'polls:detail', args=(past_question.id,) )
        response = self.client.get( url )

        self.assertContains( response, past_question.question_text )


class QuestionResultsViewTests( TestCase ):
    def test_future_question(self):
        future_question = create_question( question_text="Future question.", days=1 )

        url = reverse( 'polls:results', args=(future_question.id,) )
        response = self.client.get( url )

        self.assertEqual( response.status_code, 404 )

    def test_past_question(self):
        past_question = create_question( question_text="Past question.", days=-1 )

        url = reverse( 'polls:results', args=(past_question.id,) )
        response = self.client.get( url )

        self.assertContains( response, past_question.question_text )


class QuestionModelTests( TestCase ):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta( days=30 )
        future_question = Question( pub_date=time )

        self.assertIs( future_question.was_published_recently(), False )

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions
        more than one day old
        """
        time = timezone.now() - datetime.timedelta( days=2 )
        old_question = Question( pub_date=time )

        self.assertIs( old_question.was_published_recently(), False )

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions
        published within the last day
        """
        time = timezone.now() - datetime.timedelta( hours=6 )
        recent_question = Question( pub_date=time )

        self.assertIs( recent_question.was_published_recently(), True )
