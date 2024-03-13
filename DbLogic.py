import psycopg2

class DbLogic:
    def connect_to_db(self):
        try:
            # Change the access details to your database here
            conn = psycopg2.connect(
                dbname="crawlerdb",
                user="postgres",
                password="geslo",  # Replace 'geslo' with your actual password
                host="localhost"
            )
            print("Connected to the database.")
            return conn
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            return None

    def save_page(self, site_id, url, html_content, page_hash, http_status_code, accessed_time, page_type_code='FRONTIER'):
        conn = self.connect_to_db()
        if conn is not None:
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO crawldb.page (site_id, url, html_content, hash_value, http_status_code, accessed_time, page_type_code)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (url) DO NOTHING;
                    """, (site_id, url, html_content, page_hash, http_status_code, accessed_time, page_type_code))
                    conn.commit()
                    print(f"Saved URL: {url} with title (as HTML content): {html_content} to the database")
            except Exception as e:
                print(f"Error saving page {url}: {e}")
            finally:
                conn.close()
