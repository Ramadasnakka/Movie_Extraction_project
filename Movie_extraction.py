#Install pandas and bs4
import requests
import bs4
from collections import Counter
import math
import pandas as pd
import glob
        

def movies_name(movie_name,partial_url):
    url = f'https://www.metacritic.com/movie/{partial_url}/details'
    
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}

    res = requests.get(url,headers=headers)
    
    soup = bs4.BeautifulSoup(res.text,'lxml')
    container = soup.select('.credits')
    
    credit_set = []
    for credit in container:
        cast = [cast.getText() for cast in credit.select('.person')]
        role = [cast.getText() for cast in credit.select('.role')]
        credit = []
        for i in range(len(cast)):
            credit.extend([cast[i].strip(),role[i].strip()])
        credit_set.append(credit)

    return_value = f'The cast of the movie {movie_name} includes '
    for credits in credit_set:
        if 'Cast' in credits[0]:
            for i in range(2,len(credits),2):
                return_value += credits[i]+ ' as ' + credits[i+1] + ','
    

    movie_cast_info = return_value[:-1] + '.'  
    
    
    genre_xml = soup.select('.genres')
    
    genres = genre_xml[0].select('.data')[0].getText()
    
    for one in genre_xml:
        g = one.select('.data')
        break
    if g:
        for one in g:
            genres = one.getText()
            break

    genres = ','.join(list(map(lambda x:x.strip(),genres.split(','))))
    
    genres =  'The genre of the movie is ' + genres + '.'
    
    result = [movie_cast_info,genres]


    return result


def top_500_movies(*args,**kwargs):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
    movies_detail_info = [["Movie_name","Cast_Info","Genre_Info"]]
    movie_names = []
    cnt = 0
    for i in range(5):
        res = requests.get(f'https://www.metacritic.com/browse/movies/score/metascore/all/filtered?sort=desc&page={i}',headers=headers)

        soup = bs4.BeautifulSoup(res.text,'lxml')
        container = soup.find_all('td', class_ = 'clamp-summary-wrap')

        for movie in container:
            name = movie.find('h3').contents[0]
            partial_url = movie.find('a').get('href',None).split('/')[2]
            movie_info = movies_name(name,partial_url)
            movies_detail_info.append([name,movie_info[0],movie_info[1]])
            cnt+=1
            print(cnt)
    
            movie_names.append(name)
    return movies_detail_info
            

def genres_from_csv(actor_name):
    genres = []
    movie_names = []
    with open('..\\desktop\\Movie_Cast_data.csv',encoding='utf-8') as fp:
        for inp in fp:

            if actor_name.lower() in inp.lower():
                movie_names.append(inp.split(",")[0])
                g = inp.split("The genre of the movie is ")[-1].split(",")
                g[-1]=g[-1].replace('."\n','')
                g[-1]=g[-1].replace('.\n','')
                genres.extend(g)
    return [genres,movie_names]
    
def genres_format_to_str(actor_name,genres,movie_names):
    if not (genres and movie_names):
        return ''
    movie_str = f"The {actor_name.title()} movie names are {', '.join(movie_names)}."       
    genres_str = "The Most often played genres are "
    for genre,count in Counter(genres).items():
        genres_str+=genre+":"+str(count)+","
    genres_str = genres_str[:-1]+"."
    return movie_str+'\n'+genres_str


def cosine_calculation(actor_names):
    genres1,_ = genres_from_csv(actor_names[0])
    genres2,_ = genres_from_csv(actor_names[1])
    
    diff_genres2 = set(genres1)-set(genres2)
    diff_genres1 = set(genres2)-set(genres1)

    actor1 = Counter(genres1)
    for key in diff_genres1:
        actor1[key] = 0
    actor2 = Counter(genres2)
    for key in diff_genres2:
        actor2[key]=0

    numerator = 0
    den1 = 0
    den2 = 0
    for key in actor1:
        numerator += actor1[key] * actor2[key]
        den1 += actor1[key] **2
        den2 += actor2[key] **2
    

    cosine_value = numerator/(math.sqrt(den1)*math.sqrt(den2))

    return round(cosine_value,4)



if __name__ == "__main__":
    path = "..\\desktop\\Movie_Cast_data.csv"
    file_name = glob.glob(path)
    if not file_name:
        data = top_500_movies()
        dt = pd.DataFrame(data)
        dt.to_csv(path, index=False, header=False)
    
    while True:
        option = input("What do you want to check on Metacritics?(Please choose 'movie','people',or 'comparsion')")
        if option.lower() == 'movie':
            movie_opt = input("What movie do you want to check?")
            df = pd.read_csv(path,header=None, index_col=0, squeeze=True).to_dict()
            found = False
            for key in df[1]:
                if key.lower()==movie_opt.lower():
                    print(df[1][key])
                    print(df[2][key])
                    found= True,
                    break
            if not found:
                print("Please search the movie from top 500 movies")

        elif option.lower() == 'people':
            people_opt = input("What do you want to check? ")
            genres,movies = genres_from_csv(people_opt) if people_opt else ([],[])

            people_info = genres_format_to_str(people_opt,genres,movies)
            if not (people_info):
                print("Please select the actor from top 500 movies")
            else:
                print(people_info)

        elif option.lower() == 'comparsion':
            print("Who do you want to compare?\n ")
            act1 = input("actor 1: ")
            act2 = input("actor 2: ")
            genres1,movies1 = genres_from_csv(act1) if act1 else([],[])
            act1_info = True if genres1 and movies1 else False
            genres2,movies2 = genres_from_csv(act2) if act2 else ([],[])
            act2_info = True if genres2 and movies2 else False
            if (act1_info and act2_info):
                print(genres_format_to_str(act1,genres1,movies1),genres_format_to_str(act2,genres2,movies2),sep='\n')
                print(f"Based on that, they have cosine similarity score of {cosine_calculation([act1,act2])}")

            else:
                print("Enter the actors from top 500 movies")
        
        else:
            break
