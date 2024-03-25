import psycopg2
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class DbLogic:
    def __init__(self) -> None:
        try:
            # Change the access details to your database here
            self.conn = psycopg2.connect(
                dbname="crawlerdb",
                user="postgres",
                #password="pw",  # Replace 'geslo' with your actual password
                password="iepsDB",  
                host="localhost",
            )
            print("Connected to the database.")
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            return None
        
    def connect_to_db(self):
        try:
            # Change the access details to your database here
            conn = psycopg2.connect(
                dbname="crawldb",
                user="postgres",
                #password="pw",  # Replace 'geslo' with your actual password
                password="Jure.2000",  
                host="localhost",
            )
            print("Connected to the database.")
            return conn
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            return None
        
    def get_frontier(self):
        ##conn = self.connect_to_db()
        urls = []
        if self.conn is not None:
            try:
                with self.conn.cursor() as cur:
                    cur.execute("SELECT url FROM crawldb.page WHERE page_type_code = 'FRONTIER' ORDER BY accessed_time ASC;")
                    for row in cur.fetchall():
                        urls.append(row[0])
            except Exception as e:
                print(f"Error getting frontier: {e}")
            #finally:
                #self.conn.close()
        return urls
    
    def check_hash_exists(self, page_hash):
        ##conn = self.connect_to_db()
        if self.conn is not None:
            try:
                with self.conn.cursor() as cur:
                    # Ensure page_hash is treated as a string
                    page_hash_str = str(page_hash)
                    cur.execute("SELECT id FROM crawldb.page WHERE hash_value = %s;", (page_hash_str,))
                    page_id = cur.fetchone()
                    if page_id is not None:
                        return page_id[0]
                    else:
                        return None
            except Exception as e:
                print(f"Error checking if hash exists: {e}")
            #finally:
             #   conn.close()

    def insert_image(self, page_id, filename, content_type, data, accessed_time):
        if self.conn is not None:
            try:
                with self.conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO crawldb.image (page_id, filename, content_type, data, accessed_time)
                        VALUES (%s, %s, %s, %s, %s);
                    """, (page_id, filename, content_type, data, accessed_time))
                    self.conn.commit()
                    print(f"Image {filename} for page ID {page_id} has been saved to the database.")
            except Exception as e:
                print(f"Error saving image {filename} for page ID {page_id}: {e}")
            #finally:
                #conn.close()


    def check_page_exists(self, url):
        #conn = self.connect_to_db()
        if self.conn is not None:
            try:
                with self.conn.cursor() as cur:
                    cur.execute("SELECT id FROM crawldb.page WHERE url = %s;", (url,))
                    page_id = cur.fetchone()
                    if page_id is not None:
                        return page_id[0]
                    else:
                        return None
            except Exception as e:
                print(f"Error checking if page exists: {e}")
            #finally:
            #    conn.close()
        
    def check_site_exists(self, domain):
        #conn = self.connect_to_db()
        if self.conn is not None:
            try:
                with self.conn.cursor() as cur:
                    cur.execute("SELECT id FROM crawldb.site WHERE domain = %s;", (domain,))
                    site_id = cur.fetchone()
                    if site_id is not None:
                        return site_id[0]
                    else:
                        return None
            except Exception as e:
                print(f"Error checking if site exists: {e}")
            #finally:
            #    conn.close()


    def save_page_frontier(self, url, http_status_code, accessed_time, link_original=None):
        page_type_code = "FRONTIER"

        # Start with base query parts that do not depend on link_original
        query_columns = "url, http_status_code, accessed_time, page_type_code"
        query_values = "%s, %s, %s, %s"
        query_params = [url, http_status_code, accessed_time, page_type_code]

        # If link_original is provided (and is not None), add it to the query
        if link_original is not None:
            query_columns += ", link_original"
            query_values += ", %s"
            query_params.append(link_original)

        sql_query = f"""
            INSERT INTO crawldb.page ({query_columns})
            VALUES ({query_values})
            ON CONFLICT (url) DO NOTHING;
        """

        if self.conn is not None:
            try:
                with self.conn.cursor() as cur:
                    cur.execute(sql_query, query_params)
                    self.conn.commit()
                    print(f"Frontier URL: {url} has been saved to the database.")
            except Exception as e:
                print(f"Error saving frontier page {url}: {e}")



    def save_page_update(self, site_id, url, html_content, page_hash, page_type_code):
        #conn = self.connect_to_db()
        if self.conn is not None:
            try:
                with self.conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO crawldb.page (site_id, url, html_content, hash_value, page_type_code)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (url) DO UPDATE 
                        SET site_id = EXCLUDED.site_id,
                            html_content = EXCLUDED.html_content,
                            hash_value = EXCLUDED.hash_value,
                            page_type_code = EXCLUDED.page_type_code;
                    """, (site_id, url, html_content, page_hash, page_type_code))
                    self.conn.commit()
                    print(f"PAGE UPDATE: {url} in the database.")
            except Exception as e:
                print(f"Error saving page {url}: {e}")
            #finally:
            #    conn.close()

    def save_page_duplicate(self, url, link_original):
        #conn = self.connect_to_db()
        if self.conn is not None:
            try:
                with self.conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO crawldb.page (url, link_original)
                        VALUES (%s, %s)
                        ON CONFLICT (url) DO UPDATE
                                SET page_type_code = EXCLUDED.page_type_code;
                    """, (url, link_original))
                    self.conn.commit()
                    print(f"Duplicate URL: {url} with link {link_original} has been saved to the database.")
            except Exception as e:
                print(f"Error saving duplicate page {url}: {e}")
            #finally:
            #    conn.close()
                
    def save_link_to(self, page_id, links):
        print(f"LINKS: {links}")
        if self.conn is not None:
            try:
                with self.conn.cursor() as cur:
                    # Prepare the SQL query to update the link_to field
                    cur.execute("""
                        UPDATE crawldb.page
                        SET link_to = %s
                        WHERE id = %s;
                    """, (links, page_id))
                    self.conn.commit()
                    print(f"Links for page ID {page_id} have been updated in the database.")
            except Exception as e:
                print(f"Error updating links for page ID {page_id}: {e}")


    def save_page_binary(self, url):
        #conn = self.connect_to_db()
        if self.conn is not None:
            try:
                with self.conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO crawldb.page (url, page_type_code)
                        VALUES (%s, 'BINARY')
                        ON CONFLICT (url) DO UPDATE
                        SET page_type_code = EXCLUDED.page_type_code;
                    """, (url,))
                    self.conn.commit()
                    print(f"Binary URL: {url} has been saved to the database.")
            except Exception as e:
                print(f"Error saving binary page {url}: {e}")
            #finally:
            #    conn.close()

    def save_page_invalid(self, url):
        #conn = self.connect_to_db()
        if self.conn is not None:
            try:
                with self.conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO crawldb.page (url, page_type_code)
                        VALUES (%s, 'INVALID')
                        ON CONFLICT (url) DO UPDATE
                        SET page_type_code = EXCLUDED.page_type_code;
                    """, (url,))
                    self.conn.commit()
                    print(f"Invalid URL: {url} has been saved to the database.")
            except Exception as e:
                print(f"Error saving invalid page {url}: {e}")
            #finally:
            #    conn.close()
                
    def insert_link(self, from_page, to_page):
        if self.conn is not None:
            try:
                with self.conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO crawldb.link (from_page, to_page)
                        VALUES (%s, %s)
                    """, (from_page, to_page))
                    self.conn.commit()
                    print(f"LINK INSERTED: {from_page} -> {to_page}")
            except Exception as e:
                print(f"Error saving link {from_page} -> {to_page}: {e}")

        

    def save_page_data(self, page_id, data_type_code):

        data_type_code_upper = data_type_code.upper()
        print(f"PAGE DATA: ID->{page_id}, Data type->{data_type_code_upper}")
        #conn = self.connect_to_db()
        if self.conn is not None:
            try:
                with self.conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO crawldb.page_data (page_id, data_type_code)
                        VALUES (%s, %s);
                    """, (page_id, data_type_code_upper))
                    self.conn.commit()
                    print(f"Data type {data_type_code_upper} for page ID {page_id} has been saved to the database.")
            except Exception as e:
                print(f"Error saving page data: {e}")
            #finally:
            #    conn.close()



    def save_site(self, domain, robots_content, sitemap_content):
        #conn = self.connect_to_db()
        if self.conn is not None:
            try:
                with self.conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO crawldb.site (domain, robots_content, sitemap_content)
                        VALUES (%s, %s, %s)
                        RETURNING id;
                    """, (domain, robots_content, sitemap_content))
                    site_id = cur.fetchone()[0]
                    self.conn.commit()
                    print(f"Site with domain {domain} and ID {site_id} has been saved to the database.")
                    return site_id
            except Exception as e:
                print(f"Error saving site {domain}: {e}")
            #finally:
            #    conn.close()
