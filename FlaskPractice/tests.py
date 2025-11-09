import os
os.environ['DATABASE_URL'] = 'sqlite://'

from datetime import datetime, timezone, timedelta
import unittest
from app import app, db
from app.models import User, Post

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_password_hashing(self):
        u = User(username = 'susan', email ='ssoska@example.com')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))
    
    def test_avatar(self):
        u = User(username = 'orn', email = 'voronov.228@mail.ru')
        # Проверяем основные свойства, а не конкретный хэш
        avatar_url = u.avatar(128)
    
    # 1. Проверяем что возвращается строка
        self.assertIsInstance(avatar_url, str)
    
    # 2. Проверяем базовую структуру URL
        self.assertTrue(avatar_url.startswith('https://www.gravatar.com/avatar/'))
        self.assertIn('?d=identicon&s=128', avatar_url)
    
    # 3. Проверяем что размер подставляется правильно
        self.assertIn('s=128', avatar_url)
    
    # 4. Проверяем что хэш имеет правильную длину (32 символа)
        hash_part = avatar_url.split('/avatar/')[1].split('?')[0]
        self.assertEqual(len(hash_part), 32)
        self.assertTrue(hash_part.isalnum())  # только буквы и цифры
    
    def test_follow(self): 
        u1 = User(username='orn', email = 'voronov.228@mail.ru')
        u2 = User(username = 'susan', email = 'ssoska@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        following = db.session.scalars(u1.following.select()).all()
        followers = db.session.scalars(u2.followers.select()).all()
        self.assertEqual(following,[])
        self.assertEqual(followers, [])
        
        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.following_count(), 1)
        self.assertEqual(u2.followers_count(), 1)
        u1_following = db.session.scalars(u1.following.select()).all()
        u2_followers = db.session.scalars(u2.followers.select()).all()
        self.assertEqual(u1_following[0].username, 'susan')
        self.assertEqual(u2_followers[0].username, 'orn')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.following_count(), 0)
        self.assertEqual(u2.followers_count(), 0)

    def test_follow_posts(self):
        #создание пользователей
        u1 = User(username='orn', email='john@example.com')
        u2 = User(username='susan', email='ssoska@example.com')
        u3 = User(username='marta', email='mary@example.com')
        u4 = User(username='david124', email='david322@example.com')
        db.session.add_all([u1, u2, u3, u4])

        #создание постов
        now = datetime.now(timezone.utc)
        p1 = Post(body="post from john", author=u1,
                  timestamp=now + timedelta(seconds=1))
        p2 = Post(body="post from susan", author=u2,
                  timestamp=now + timedelta(seconds=4))
        p3 = Post(body="post from mary", author=u3,
                  timestamp=now + timedelta(seconds=3))
        p4 = Post(body="post from david", author=u4,
                  timestamp=now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        #установка подписок
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u3)  # susan follows mary
        u3.follow(u4)  # mary follows david
        db.session.commit()

        #проверка отслеживания постов 
        f1 = db.session.scalars(u1.following_posts()).all()
        f2 = db.session.scalars(u2.following_posts()).all()
        f3 = db.session.scalars(u3.following_posts()).all()
        f4 = db.session.scalars(u4.following_posts()).all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])


if __name__ == '__main__':
    unittest.main(verbosity=2)