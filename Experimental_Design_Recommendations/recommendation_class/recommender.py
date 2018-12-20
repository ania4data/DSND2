import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
#!pip install progressbar
import progressbar
import sys # can use sys to take command line arguments
import recommender_functions_utils as rf

class Recommender():
    '''
    This Recommender uses FunkSVD, rank-based, mix(FunkSVD+rank-based) model for users,
    as well as content-base method for movies to make recommnedation. 
    Also uses either FunkSVD or mix method to make prediction on review rating for particular user and movie. 
    '''
    def __init__(self, method='mix', _idtype='user', latent_features=12, learning_rate=0.0001, iters=500, rec_num=5, print_every=10):
        '''
        This function initialize the class
        INPUT:
        method - (str) 'mix': funk-SVD+rank-base, 'funk-SVD', 'rank-base', 'content-base'
        _idtype - (str) 'user' or 'movie'
                        'user' only compatible with 'mix'/'funk-SVD'/'rank-base' methods
                        'movie' only compatible with 'content-base' methods

        latent_features - (int) the number of latent features used in 'mix'/funk-SVD' methods
        learning_rate - (float) the learning rate in 'mix'/funk-SVD' methods
        iters - (int) the number of iterations in 'mix'/funk-SVD' methods
        rec_num - (int) number of recommendations for output
        print_every - (int) interval between prints in 'mix'/funk-SVD' methods

        OUTPUT:
        None - stores the following as attributes:
        method - (str) 'mix': funk-SVD+rank-base, 'funk-SVD', 'rank-base', 'content-base'
        _idtype - (str) 'user' or 'movie'
                        'user' only compatible with 'mix'/'funk-SVD'/'rank-base' methods
                        'movie' only compatible with 'content-base' methods

        latent_features - (int) the number of latent features used in 'mix'/funk-SVD' methods
        learning_rate - (float) the learning rate in 'mix'/funk-SVD' methods
        iters - (int) the number of iterations in 'mix'/funk-SVD' methods
        rec_num - (int) number of recommendations for output
        print_every - (int) interval between prints in 'mix'/funk-SVD' methods
        review - review dataframe
        movies - movies dataframe
        train_user_item - reviews with fewer columns
        movie_ids_list - list of movies in movies dataframe
        user_ids_series - list of users in review datafarame
        movie_ids_series - list of movies in review dataframe
        dot_prod_movies_df - movie similarity (dot product) of categories in dataframe
        ranked_movies - review-movie join dataframe ordered by abg rating, date, with more than 4 review
        user_mat - user * latent_feature matrix from SVD/mix
        movie_mat -  latent_feature * movie matrix from SVD/mix
        '''

        self.method = method
        self._idtype = _idtype
        self.latent_features = latent_features
        self.learning_rate = learning_rate
        self.iters = iters
        self.rec_num = rec_num
        self.print_every = print_every

        if((self._idtype == 'user') and (self.method not in ['mix', 'funk-SVD', 'rank-base'])):
            print("For 'user' idtype must initialize with one of 'mix'/'funk-SVD'/'rank-base' methods")
            print("By default set method to 'mix'")
            self.method = 'mix'

        if((self._idtype == 'movie') and (self.method not in ['content-base'])):
            print("For 'movie' idtype must initialize with 'content-base'")
            print("By default set method to 'content-base'")
            self.method = 'content-base'
 
    def fit(self, movies, reviews):
        '''
        fit the recommender to your dataset and also have this save the results
        to pull from when you need to make predictions
        '''
        self.reviews = reviews
        self.movies = movies

        self.train_user_item = self.reviews[['user_id', 'movie_id', 'rating', 'timestamp']]
        movie_content = np.array(self.movies.iloc[:,4:])
        print('Fitting .......')
        print('Method: {} id_type: {}'.format(self.method, self._idtype))
        print()
        if(self._idtype == 'movie'):
            if(self.method == 'content-base'):
                dot_prod_movies = movie_content.dot(np.transpose(movie_content))
                self.movie_ids_list = self.movies.movie_id.values
                self.dot_prod_movies_df = pd.DataFrame(dot_prod_movies, columns=self.movie_ids_list, index=self.movie_ids_list)

        if(self._idtype == 'user'):
            if((self.method == 'mix') or (self.method == 'rank-base')):
                self.ranked_movies = rf.create_ranked_df(self.movies, self.reviews)

            if((self.method == 'mix') or (self.method == 'funk-SVD')):
                # user/movie matrix with rating in bulk
                self.train_data_df = self.train_user_item.groupby(['user_id', 'movie_id'])['rating'].max().unstack()
                self.user_ids_series = np.array(self.train_data_df.index)
                #print(8 in self.user_ids_series)
                self.movie_ids_series = np.array(self.train_data_df.columns)
                self.train_data_np = np.array(self.train_data_df)
                self.user_mat, self.movie_mat = rf.FunkSVD(self.train_data_np, self.latent_features, self.learning_rate, self.iters, self.print_every)

           

    def predict(self, user_id, movie_id):
        '''
        INPUT:
        user_id - the user_id from the reviews df
        movie_id - the movie_id according the movies df

        OUTPUT:
        rating - the predicted rating for user_id-movie_id according to FunkSVD
        '''
        print()
        print('Predicting .......')
        print('Method: {} id_type: {}'.format(self.method, self._idtype))
        print()        

        if((self._idtype == 'user') and ((self.method=='mix') or (self.method=='funk-SVD'))):

            try:       
                rating = rf.predict_rating(self.train_data_df, self.user_mat, self.movie_mat, user_id, movie_id)
                print('For user_id: {} and movie_id: {} ({})'.format(user_id, movie_id, rf.get_movie_names([movie_id], self.movies)[0]))
                print('Rating is: {}'.format(np.round(rating,2)))
                return rating

            except:
                print("No prediction can be made for {} user_id and {} movie_id, try another combo".format(user_id, movie_id))
                return None

        else:
            print("No prediction can be made for {} idtype and {} method".format(self._idtype, self.method))
            return None


    def make_recommendations(self, _id):
        '''
        INPUT:
        _id - either a user or movie id (int), depends on method

        OUTPUT:
        rec_ids - (array) a list or numpy array of recommended movies like the
                       given movie, or recs for a user_id given
        rec_names - (list) a list of recommended movie names              
        '''
        print()
        print('Making recommendation .......')
        print('Method: {} id_type: {}'.format(self.method, self._idtype))
        print()        
        if(self._idtype == 'movie'):

            try:
                rec_ids_tmp = rf.find_similar_movies(_id, self.dot_prod_movies_df)[0: 2*self.rec_num]
                self.rec_ids = np.random.choice(rec_ids_tmp, self.rec_num, replace=False)
                self.rec_names = rf.get_movie_names(self.rec_ids, self.movies)
            except:
                print('movie_id: {} not found, try another one'.format(_id))
                return None


        if(self._idtype == 'user'):
            if(self.method=='rank-base'):
                
                rec_ids_tmp = rf.popular_recommendations(_id, 2*self.rec_num, self.ranked_movies) 
            # create some surprise
                self.rec_ids = np.random.choice(rec_ids_tmp, self.rec_num, replace=False)
                self.rec_names = rf.get_movie_names(self.rec_ids, self.movies)

            if(self.method=='funk-SVD'):

                if(_id in self.user_ids_series):
                    #funk svd recomm
                    user_unseen_movie_id = rf.svd_recommendation(_id, self.train_data_df, self.user_mat, self.movie_mat, self.rec_num)
                    self.rec_ids = np.random.choice(user_unseen_movie_id, self.rec_num, replace=False)
                    self.rec_names = rf.get_movie_names(self.rec_ids, self.movies)
                else:
                    print('user_id: {} not found, try another one'.format(_id))
                    return None

            if(self.method=='mix'):
                if(_id in self.user_ids_series):
                    user_unseen_movie_id = rf.svd_recommendation(_id, self.train_data_df, self.user_mat, self.movie_mat, self.rec_num)
                    self.rec_ids = np.random.choice(user_unseen_movie_id, self.rec_num, replace=False)
                    self.rec_names = rf.get_movie_names(self.rec_ids, self.movies)
                if(_id not in self.user_ids_series):
                    rec_ids_tmp = rf.popular_recommendations(_id, 2*self.rec_num, self.ranked_movies)
                    self.rec_ids = np.random.choice(rec_ids_tmp, self.rec_num, replace=False)
                    self.rec_names = rf.get_movie_names(self.rec_ids, self.movies)

        return self.rec_ids, self.rec_names

if __name__ == '__main__':
    # test different parts to make sure it works

    movies_, reviews_ = rf.load_data('train_data.csv', 'movies_clean.csv')

    # Method mix
    print('Method mix-------------------------------------------------')
    rec = Recommender(method='mix', iters=20, print_every=1)
    #print('here')
    rec.fit(movies=movies_, reviews=reviews_)
    rec.predict(user_id=8, movie_id=2844)
    rec.predict(user_id=1, movie_id=2844)
    print(rec.make_recommendations(8))  # in data
    print(rec.make_recommendations(1))  # not in data

    # Method rank-base
    print('Method rank-base--------------------------------------------')
    rec2 = Recommender(method='rank-base', iters=20, print_every=1)
    #print('here')
    rec2.fit(movies=movies_, reviews=reviews_)
    rec2.predict(user_id=8, movie_id=2844)
    rec2.predict(user_id=1, movie_id=2844)
    print(rec2.make_recommendations(8))
    print(rec2.make_recommendations(1))

    print('Method funk-SVD--------------------------------------------')
    rec3 = Recommender(method='funk-SVD', iters=20, print_every=1)
    #print('here')
    rec3.fit(movies=movies_, reviews=reviews_)
    rec3.predict(user_id=8, movie_id=2844)
    rec3.predict(user_id=1, movie_id=2844)
    print(rec3.make_recommendations(8))
    print(rec3.make_recommendations(1))

    print('Method content-base--------------------------------------------')
    rec4 = Recommender(method='content-base', _idtype='movie', iters=20, print_every=1)
    #print('here')
    rec4.fit(movies=movies_, reviews=reviews_)
    rec4.predict(user_id=8, movie_id=2844)
    rec4.predict(user_id=1, movie_id=2844)
    print(rec4.make_recommendations(8))
    print(rec4.make_recommendations(1))
