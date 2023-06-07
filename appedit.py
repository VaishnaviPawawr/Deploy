import streamlit as st
import pickle
import urllib.parse
import requests
from streamlit_lottie import st_lottie


st.set_page_config(page_title="BRS", page_icon=":tada:", layout="wide")


#Designing  ## function to access animation
def load_lottieURL(url):
    r = requests.get(url)
    if r.status_code !=200:
        return None
    return r.json()

#Animations
Animation1 = load_lottieURL("https://assets10.lottiefiles.com/private_files/lf30_ipvphpwo.json")
Animation2 = load_lottieURL("https://assets2.lottiefiles.com/private_files/lf30_5qccdrpm.json")
Animation3 = load_lottieURL("https://assets6.lottiefiles.com/private_files/lf30_x8aowqs9.json")

#WEB FUNCITONALLITY
with open("updated_recommendation_pickle.pkl", "rb") as file:
    pickle_data = pickle.load(file)

    
#HYBRID MODEL
def hybrid_recommend(book_name):
    # Content-based filtering
    book_features_subset = pickle_data[9][pickle_data[9]['bookTitle'] == book_name]
    if book_features_subset.empty:
        return []  # Return empty lis if book not found in book features
    book_subset_indices = book_features_subset.index.tolist()
    book_subset_similarity_scores = pickle_data[8][:, book_subset_indices].flatten()
    content_based_scores = list(enumerate(book_subset_similarity_scores))

    # Collaborative filtering
    collaborative_scores = list(enumerate(pickle_data[8][pickle_data[7].index == book_name].flatten()))

    # Combine scores from both approaches
    combined_scores = [(idx, content_based_scores[idx][1] + collaborative_scores[idx][1]) for idx in range(len(content_based_scores))]

    # Sort the combined scores
    combined_scores = sorted(combined_scores, key=lambda x: x[1], reverse=True)[:6]

    # Retrieve recommended books
    recommended_books = []
    for i in combined_scores:
        temp_df = pickle_data[0][pickle_data[0]['bookTitle'] == pickle_data[7].index[i[0]]]
        recommended_books.append((temp_df['bookTitle'].values[0], temp_df['bookAuthor'].values[0], temp_df['imageUrlM'].values[0]))
    
    return recommended_books

def recommend_for_user(userID):
    l2 = []
    if userID in pickle_data[6]['userId'].unique():
        # User exists in the dataset, recommend based on their ratings
        user_books = pickle_data[6].loc[pickle_data[6]['userId'] == userID]['bookTitle'].values[:3]
        for book in user_books:
            recommendations = hybrid_recommend(book)
            l2.extend(recommendations[:3])  # Take the top 2 recommendations for each book
        return l2
    else:
        # User not found in the dataset, recommend the most rated book
        most_rated_book = pickle_data[6].groupby('bookTitle').count().sort_values('bookRating', ascending=False).index[0:10]
        l1 = list(most_rated_book)
        for i in l1:
            l2.append((i, pickle_data[6].loc[pickle_data[6]['bookTitle'] == i]['bookAuthor'].values[0], pickle_data[6].loc[pickle_data[6]['bookTitle'] == i]['imageUrlM'].values[0]))
        return l2

#Books to be displayed in app
def display_all_books(books):
    st.title("Recommendations for You!")
    for book in books:
        with st.container():
            left_column, right_column = st.columns(2)
        with left_column:
            search_url = "[Click here to visit]" + "(https://www.goodreads.com/search?q=" + urllib.parse.quote_plus(book[0]) +")"
            st.subheader(book[0]) 
            st.markdown(search_url)
            st.write("Author:", book[1]) 
        with right_column:
            st.image(book[2])  
        st.write("---")  # Add a horizontal line

        
#WEBAPP STARTED HERE
# Create the navbar
st.sidebar.title("MENU")
nav_selection = st.sidebar.radio("Go to", ("Recommender System","Book Search", "Data visualization", "Reference"))

# Display different content based on the navbar selection
if nav_selection == "Recommender System":
    with st.container():
        left_column, right_column = st.columns(2)
    with left_column:
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.title("This is Book Recommender System")   
    with right_column:
        st_lottie(Animation1,key="coding",height=310)
    # Add content for the home page
    form = st.form(key='my_form')
    UserID = form.text_input(label='Enter UserID')
    submit_button = form.form_submit_button(label='Submit')
    if (submit_button & (len(UserID)!=0)):
        st.write(f'Welcome user. Your User ID is : {UserID}')
        book_data = recommend_for_user(int(UserID))
        display_all_books(book_data)
    