import psycopg2
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class DbLogic:
    def connect_to_db(self):
        try:
            # Change the access details to your database here
            conn = psycopg2.connect(
                dbname="crawlerdb",
                user="postgres",
                #password="pw",  # Replace 'geslo' with your actual password
                password="iepsDB",  
                host="localhost",
            )
            print("Connected to the database.")
            return conn
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            return None
        
    def get_frontier(self):
        conn = self.connect_to_db()
        urls = []
        if conn is not None:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT url FROM crawldb.page WHERE page_type_code = 'FRONTIER' ORDER BY accessed_time ASC;")
                    for row in cur.fetchall():
                        urls.append(row[0])
                    print(f"Frontier URLs in DB function: {urls}")
            except Exception as e:
                print(f"Error getting frontier: {e}")
            finally:
                conn.close()
        return urls

    def check_page_exists(self, url):
        conn = self.connect_to_db()
        if conn is not None:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM crawldb.page WHERE url = %s;", (url,))
                    page_id = cur.fetchone()
                    if page_id is not None:
                        return page_id[0]
                    else:
                        return None
            except Exception as e:
                print(f"Error checking if page exists: {e}")
            finally:
                conn.close()
        
    def check_site_exists(self, domain):
        conn = self.connect_to_db()
        if conn is not None:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM crawldb.site WHERE domain = %s;", (domain,))
                    site_id = cur.fetchone()
                    if site_id is not None:
                        return site_id[0]
                    else:
                        return None
            except Exception as e:
                print(f"Error checking if site exists: {e}")
            finally:
                conn.close()

    def save_page(self, site_id, url, html_content, page_hash, http_status_code, accessed_time, page_type_code):
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
                    #print(f"Saved URL: {url}, HASH: {page_hash}, HTML CONTENT: {html_content} ACCESSED TIME: {accessed_time} to the database")
            except Exception as e:
                print(f"Error saving page {url}: {e}")
            finally:
                conn.close()

    def save_page_frontier(self, url, http_status_code, accessed_time):
        conn = self.connect_to_db()
        page_type_code = "FRONTIER"

        if conn is not None:
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO crawldb.page (url, http_status_code, accessed_time, page_type_code)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (url) DO NOTHING;
                    """, (url, http_status_code, accessed_time, page_type_code))
                    conn.commit()
                    print(f"Frontier URL: {url} has been saved to the database.")
            except Exception as e:
                print(f"Error saving frontier page {url}: {e}")
            finally:
                conn.close()


    def save_page_update(self, site_id, url, html_content, page_hash, page_type_code):
        conn = self.connect_to_db()
        if conn is not None:
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO crawldb.page (site_id, url, html_content, hash_value, page_type_code)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (url) DO UPDATE 
                        SET site_id = EXCLUDED.site_id,
                            html_content = EXCLUDED.html_content,
                            hash_value = EXCLUDED.hash_value,
                            page_type_code = EXCLUDED.page_type_code;
                    """, (site_id, url, html_content, page_hash, page_type_code))
                    conn.commit()
                    print(f"PAGE UPDATE: {url} in the database.")
            except Exception as e:
                print(f"Error saving page {url}: {e}")
            finally:
                conn.close()

    def save_page_binary(self, url):
        conn = self.connect_to_db()
        if conn is not None:
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO crawldb.page (url, page_type_code)
                        VALUES (%s, 'BINARY')
                        ON CONFLICT (url) DO UPDATE
                        SET page_type_code = EXCLUDED.page_type_code;
                    """, (url,))
                    conn.commit()
                    print(f"Binary URL: {url} has been saved to the database.")
            except Exception as e:
                print(f"Error saving binary page {url}: {e}")
            finally:
                conn.close()


    def save_site(self, domain, robots_content):
        conn = self.connect_to_db()
        if conn is not None:
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO crawldb.site (domain, robots_content)
                        VALUES (%s, %s)
                        RETURNING id;
                    """, (domain, robots_content))
                    site_id = cur.fetchone()[0]
                    conn.commit()
                    print(f"Site with domain {domain} and ID {site_id} has been saved to the database.")
                    return site_id
            except Exception as e:
                print(f"Error saving site {domain}: {e}")
            finally:
                conn.close()
