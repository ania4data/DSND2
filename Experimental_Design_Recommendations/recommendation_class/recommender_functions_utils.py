import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt

def load_data(reviews_pth, movies_pth):
    '''
    INPUT
    reviews_pth (str)- path to review csv file
    movies_pth (str) - path to movie csv file
    OUTPUT
    reviews - review dataframe
    movies - movie dataframe
    '''
    reviews = pd.read_csv(reviews_pth)
    movies = pd.read_csv(movies_pth)

    del movies['Unnamed: 0']
    del reviews['Unnamed: 0']

    return movies, reviews

def FunkSVD(ratings_mat, latent_features=4, learning_rate=0.0001, iters=100, print_every = 10):
    '''
    This function performs matrix factorization using a basic form of FunkSVD with no regularization
    
    INPUT:
    ratings_mat - (numpy array) a matrix with users as rows, movies as columns, and ratings as values
    latent_features - (int) the number of latent features used
    learning_rate - (float) the learning rate 
    iters - (int) the number of iterations
    print_every - (int) the number of intervals between prints
    
    OUTPUT:
    user_mat - (numpy array) a user by latent feature matrix
    movie_mat - (numpy array) a latent feature by movie matrix
    '''
    
    # Set up useful values to be used through the rest of the function
    n_users = ratings_mat.shape[0]
    n_movies = ratings_mat.shape[1]
    num_ratings = n_users * n_movies
    
    # initialize the user and movie matrices with random values
    user_mat = np.random.rand(n_users, latent_features)  # user matrix filled with random values of shape user x latent 
    movie_mat = np.random.rand(latent_features, n_movies) # movie matrix filled with random values of shape latent x movies
    
    # initialize sse at 0 for first iteration
    sse_accum = 0
    
    # header for running results
    print("Optimization Statistics")
    print("Iterations | Mean Squared Error ")
    
    user_movie_index = []
    for user_i in range(n_users):
        for movie_j in range(n_movies):
            if(math.isnan(ratings_mat[user_i,movie_j])==False):
                user_movie_index.append([user_i,movie_j])

    sse = []
    for t in range(iters):
        
        # update our sse
        old_sse = sse_accum
        sse_accum = 0
                
        for pairs in user_movie_index:
            user_i = pairs[0]
            movie_j = pairs[1]

            # dot product
            uv_new = np.dot(user_mat[user_i,:], movie_mat[:,movie_j])
            delta = (ratings_mat[user_i, movie_j] - uv_new)
            #print(delta)
            sse_accum += delta**2.0 #sum of the square error

            for k in range(latent_features):
                user_mat[user_i,k] = user_mat[user_i,k] + 2.0 * (delta) * learning_rate * movie_mat[k,movie_j]
                movie_mat[k,movie_j] = movie_mat[k,movie_j] + 2.0 * (delta) * learning_rate * user_mat[user_i,k]  
            

        sse.append(sse_accum)
        if(t%print_every==0):
            print('iteration {}: sse_accum {}'.format(t+1, np.round(sse_accum,1)))
    plt.plot(sse)  
    plt.title('iteration {}: sse_accum {}, learning rate {}'.format(t+1, sse_accum, learning_rate))
    plt.show()
    return user_mat, movie_mat 


def predict_rating(train_data_df, user_matrix, movie_matrix, user_id, movie_id):
    '''
    INPUT:
    train_data_df - user/movie unstack dataframe
    user_matrix - user by latent factor matrix
    movie_matrix - latent factor by movie matrix
    user_id - the user_id from the reviews df
    movie_id - the movie_id according the movies df
    
    OUTPUT:
    pred - the predicted rating for user_id-movie_id according to FunkSVD
    '''
    # Create series of users and movies in the right order
    user_ids_series = np.array(train_data_df.index)
    movie_ids_series = np.array(train_data_df.columns)
    
    # User row and Movie Column
    user_row = np.where(user_ids_series == user_id)[0][0]
    movie_col = np.where(movie_ids_series == movie_id)[0][0]
    
    # Take dot product of that row and column in U and V to make prediction
    pred = np.dot(user_matrix[user_row, :], movie_matrix[:, movie_col])
    
    return pred


def get_movie_names(movie_ids, movies_df):
    '''
    INPUT
    movie_ids - a list of movie_ids
    movies_df - original movies dataframe
    OUTPUT
    movies - a list of movie names associated with the movie_ids

    '''
    # Read in the datasets
    movie_lst = list(movies_df[movies_df['movie_id'].isin(movie_ids)]['movie'])

    return movie_lst


def create_ranked_df(movies, reviews):
        '''
        INPUT
        movies - the movies dataframe
        reviews - the reviews dataframe

        OUTPUT
        ranked_movies - a dataframe with movies that are sorted by highest avg rating, more reviews, then time, and must have more than 4 ratings
        '''

        # Pull the average ratings and number of ratings for each movie
        movie_ratings = reviews.groupby('movie_id')['rating']
        avg_ratings = movie_ratings.mean()
        num_ratings = movie_ratings.count()
        last_rating = pd.DataFrame(reviews.groupby('movie_id').max()['date'])
        last_rating.columns = ['last_rating']

        # Add Dates
        rating_count_df = pd.DataFrame({'avg_rating': avg_ratings, 'num_ratings': num_ratings})
        rating_count_df = rating_count_df.join(last_rating)

        # merge with the movies dataset
        movie_recs = movies.set_index('movie_id').join(rating_count_df)

        # sort by top avg rating and number of ratings
        ranked_movies = movie_recs.sort_values(['avg_rating', 'num_ratings', 'last_rating'], ascending=False)

        # for edge cases - subset the movie list to those with only 5 or more reviews
        ranked_movies = ranked_movies[ranked_movies['num_ratings'] > 4]

        return ranked_movies


def find_similar_movies(movie_id, dot_prod_movies_df):
    '''
    INPUT
    movie_id - a movie_id
    dot_prod_movies_df - dot product of movie_content (categories)
    OUTPUT
    similar_movies - an array of the most similar movies (ased on their category) by id
    '''
    # dot product to get similar movies

    movie_ids_list = dot_prod_movies_df.index
    # get similarity from maxx
    tmp = dot_prod_movies_df.loc[movie_id].sort_values(ascending=False)
    # maximum correlation exclusing itself
    max_sim = tmp[tmp.index!=movie_id].max()
    arr = (tmp==max_sim)
    movie_id_list = np.array(arr[arr ==True].index)
    similar_max = np.setdiff1d(movie_id_list,[movie_id],assume_unique=True) # drop itself
    # get similarity from rest        
    arr = ((tmp>max_sim/2.0) & (tmp!=max_sim))
    movie_id_list = np.array(arr[arr ==True].index)
    # take the overlap from max list
    similar_other = np.setdiff1d(movie_id_list, similar_max, assume_unique=True)
    similar_other = np.setdiff1d(similar_other, [movie_id], assume_unique=True)
    #priority is with max index
    similar_movies = np.append(similar_max, similar_other)

    return similar_movies


def popular_recommendations(user_id, n_top, ranked_movies):
    '''
    INPUT:
    user_id - the user_id (str) of the individual you are making recommendations for
    n_top - an integer of the number recommendations you want back
    ranked_movies - a pandas dataframe of the already ranked movies based on avg rating, count, and time

    OUTPUT:
    top_movies - a list of the n_top recommended movies by movie id in order best to worst
    '''

    top_movies = list(ranked_movies.reset_index()['movie_id'][:n_top])

    return top_movies

def svd_recommendation(_id, train_data_df, user_mat, movie_mat, rec_num):
    '''
    INPUT:
    _id - (int) id of user that we want recommendation
    train_data_df - user/movie unstack dataframe
    user_mat - user by latent factor matrix
    movie_mat - latent factor by movie matrix   
    rec_num - (int) number of recommendation

    OUTPUT:
    user_unseen_movie_id - a list top rec_num movie ids with high prediction from svd 
                           that user has not seen
    '''

    user_ids_series = np.array(train_data_df.index)
    movie_ids_series = np.array(train_data_df.columns) 
    predict_array = []
    x =train_data_df.loc[_id]
    user_seen_movie = np.array(x[~train_data_df.loc[_id].isnull()].index)
    # remove movies if user already seen it
    user_unseen_movie_id = np.setdiff1d(movie_ids_series, user_seen_movie)
    user_row = np.where(user_ids_series == _id)[0][0]
    prediction = np.dot(user_mat[user_row, :], movie_mat)
    bool_unseen = np.isin(movie_ids_series, user_unseen_movie_id)
    ix = np.where(bool_unseen)
    prediction = prediction[bool_unseen]
    idx = np.argsort(prediction)[::-1]
    # sorted unseen movies
    user_unseen_movie_id = user_unseen_movie_id[idx]
    # twice as needed
    user_unseen_movie_id = user_unseen_movie_id[0:2*rec_num]

    return user_unseen_movie_id