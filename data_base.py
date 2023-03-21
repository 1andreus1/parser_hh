class DataBase(object):
    def __init__(self):
        self.credential = {
            'user': '***',
            'password': '***',
            'host': '***',
            'port': '***',
            'database': '***',
        }

    def add_to_database(self, resumes):
        sql = '''INSERT INTO resumes 
                (
                    updated_at, 
                    area_id, 
                    area_name, 
                    age, 
                    title, 
                    gender_id, 
                    salary_amount, 
                    salary_currency, 
                    photo_medium, 
                    url,
                    education, 
                    experience,
                    resume_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (resume_id) DO NOTHING;'''

        self._request(sql, values=resumes, many=True)

    def create_db(self):
        sql = '''CREATE TABLE IF NOT EXISTS resumes
                (
                    id SERIAL PRIMARY KEY,
                    updated_at text, 
                    area_id text, 
                    area_name text, 
                    age text, 
                    title text, 
                    gender_id text, 
                    salary_amount text, 
                    salary_currency text, 
                    photo_medium text, 
                    url text,
                    education text, 
                    experience text,
                    resume_id text UNIQUE
                );'''
        self._request(sql)

    def delete_database(self):
        sql = "DROP TABLE IF EXISTS resumes;"
        self._request(sql)

    def clear_database(self):
        sql = "truncate resumes;"
        self._request(sql)

    def get_count(self):
        sql = "SELECT count(*) FROM resumes;"
        return self._request(sql, fetch=True)[0][0]

    def _request(self, sql, fetch=False, values=None, many=False):
        # Запрос к БД
        cursor, conn = self.open_connection()
        try:
            if many:
                cursor.executemany(sql, values)
            else:
                cursor.execute(sql)

            if fetch:
                return cursor.fetchall()
        except (Exception, Error) as error:
            log.exception(f'Ошибка при работе с PostgreSQL\n{sql}\n{error}')
        finally:
            self.close_connection(cursor, conn)

    def open_connection(self):
        conn = psycopg2.connect(**self.credential)
        conn.set_isolation_level(isolation)
        cursor = conn.cursor()
        return cursor, conn

    @staticmethod
    def close_connection(cursor=None, conn=None):
        try:
            cursor.close()
            conn.close()
        except:
            pass