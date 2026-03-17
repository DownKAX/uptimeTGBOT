"""fill_test_data_users_table

Revision ID: 6f2ef717721c
Revises: 819b67f4bd63
Create Date: 2026-01-06 16:04:28.678517

"""

from datetime import datetime, timedelta
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import table, column, Integer, String, DateTime, BigInteger

# revision identifiers, used by Alembic.
revision: str = '6f2ef717721c'
down_revision: Union[str, None] = '819b67f4bd63'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

user_table = table('users',
          column('id', Integer),
                   column('username', String),
                   column('password', String),
                   column('email', String),
                   column('telegram_id', BigInteger),
                   column('register_time', DateTime))

def upgrade() -> None:
    time = datetime(2025, 7, 20, 15, 56, 40)
    pswds = {'user1234': '$2b$12$f/T9.upS6mbI.wqAgyPKjuGvNETPxAm886qXlJCJISWr32owQ888u',
             'user5467': '$2b$12$wx2FbFQ3EZSnbFjkmZ6ZtOz8wdXvJFmgsGKv60WEOl4jKj2ytjzqW',
             'user5357': '$2b$12$m5bM.hkLbzE6GLgg2vLjeOqH2MkkgjZKaTQGUYMKEz.MrgIH3/Je6'}

    test_data_users = [{'username': 'user', 'password': pswds['user1234'], 'email': 'user1@mail.ru', 'telegram_id': 13452345, 'register_time': time},
                       {'username': 'user1', 'password': pswds['user5467'], 'email': 'user2@mail.ru', 'telegram_id': 134524324345, 'register_time': time + timedelta(hours=1)},
                       {'username': 'user2', 'password': pswds['user5357'], 'email': 'user3@mail.ru', 'telegram_id': 1344534252345, 'register_time': time + timedelta(hours=2)}]

    op.bulk_insert(user_table, test_data_users)

def downgrade() -> None:
    op.execute('TRUNCATE TABLE users RESTART IDENTITY CASCADE;')
