from final import *
import unittest

class TestDatabase(unittest.TestCase):

    def test_artist_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = "SELECT Country FROM 'Top Artists'"
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Mexico',), result_list)

        sql = '''
            SELECT Country, Name
            FROM "Top Artists"
            WHERE Country= "Nepal"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
#        print(result_list)
        self.assertEqual(len(result_list), 50)
        self.assertEqual(result_list[0][1], 'Pink Floyd')

        conn.close()


class checkplots(unittest.TestCase):
    
    def checkbarArtists(self):
        country1 = 'Nepal'
        country2 = 'India'
        
        try:
            country_bar_plot(country1)
            country_bar_plot(country2)
        except:
            self.fail()
    
    def checkpiplot(self):
        country1 = 'Nepal'
        country2 = 'India'
        country3 = 'Thailand'
        country4 = 'Mexico'
        country5 = 'Spain'
        
        try:
            compare_countries(country1, country2, country3, country4, country5)
        except:
            self.fail()

        
if __name__ == '__main__':
    unittest.main()
