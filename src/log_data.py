import sqlite3
import pandas as pd

con = sqlite3.connect("data/main_database.db")

  





def log_key_pressed(key_pressed):
    column_names = ['key', 'correct_key', 'time', 'game_id']
    df_keys = pd.DataFrame(key_pressed, columns=column_names)
    df_keys.to_sql('keys_pressed', con, if_exists='append', index=False)


def log_game_settings(game_settings):
    column_names = ['game_id', 'game_settings']
    # game_settings_lst = [game_settings['game_id'], str({key:value if key != 'game_id'game_settings})]
    game_id = game_settings['game_id']
    del game_settings['game_id']
    df_game_settings = pd.DataFrame([[game_id, str(game_settings)]], columns=column_names)
    df_game_settings.to_sql('games_settings', con, if_exists='append', index=False)


def clean_games_settings():
    df = pd.read_sql_query('select distinct * from games_settings', con)
    df['game_settings'] = df['game_settings'].apply(lambda x: eval(x))
    df_games_settings = pd.concat([df[['game_id']], df['game_settings']\
                          .apply(lambda x: pd.Series(x))], axis=1)
    df_games_settings.drop_duplicates().to_sql('clean_games_settings', con, if_exists='replace', index=False)


def log_summary_per_game(): 
    query = f"""
        select
            distinct
            kp.game_id
            , max(kp.time) maxdatetime_unix
            , min(kp.time) mindatetime_unix
            , datetime(max(kp.time), 'unixepoch', 'localtime') as date_time
            , max(kp.time) - min(kp.time) as game_duration
            , sum(case when kp.correct_key = 1 then 1 else 0 end) as keys_to_press
            , count(*) as keys_pressed
            , round(CAST(sum(case when kp.correct_key = 1 then 1 else 0 end) as REAL) / count(*), 3) as accuracy
            , sum(case when kp.correct_key = 1 then 1 else 0 end) / ((max(kp.time) - min(kp.time)) / 60) / 5 as wpm
            , length(cgs.sentence) as sentence_length
            , length(cgs.sentence) * (sum(case when kp.correct_key = 1 then 1 else 0 end) / ((max(kp.time) - min(kp.time)) / 60) / 5) * round(CAST(sum(case when kp.correct_key = 1 then 1 else 0 end) as REAL) / count(*), 3) as score
            , cgs.sentence
            , cgs.word_count
            , coalesce(cgs.max_word_length, 1000)
            , coalesce(cgs.min_word_length, 0) 
            , coalesce(cgs.capitalized_words_count, 0)
            , coalesce(cgs.capitalized_letters_count_perc, 0)
            , coalesce(cgs.punctuation_word_count_perc, 0)
            , coalesce(cgs.force_shift, False)	
            , coalesce(cgs.hard_mode, False)
            , coalesce(cgs.train_letters, False)
            , coalesce(cgs.train_letters_easy_mode, False) as train_letters_easy_mode
            , LOWER(cgs.player_name) 

        from keys_pressed kp 
        left join clean_games_settings cgs using(game_id)
        where 1=1
        group by 1
        order by maxdatetime_unix asc
        """

    df_high_score = pd.read_sql_query(query, con)

    # Idk why but some columns can't have as new_col_name
    df_high_score = df_high_score.rename({'coalesce(cgs.max_word_length, 1000)': 'max_word_length',
                                          'coalesce(cgs.min_word_length, 0)': 'min_word_length',
                                          'LOWER(cgs.player_name)': 'player_name',
                                          'coalesce(cgs.force_shift, False)': 'force_shift',
                                          'coalesce(cgs.train_letters, False)': 'train_letters',
                                          'coalesce(cgs.capitalized_words_count, 0)': 'capitalized_words_count',
                                          'coalesce(cgs.capitalized_letters_count_perc, 0)': 'capitalized_letters_count_perc',
                                          'coalesce(cgs.punctuation_word_count_perc, 0)': 'punctuation_word_count_perc',
                                          'coalesce(cgs.hard_mode, False)': 'hard_mode'}, axis=1)
    df_high_score.to_sql('summary_per_game', con, if_exists='replace', index=False)




def push_to_gbq():
    '''Pushes the data about a specific game to BigQuery. 
    For how to authenticate, see the Google Cloud doc https://cloud.google.com/bigquery/docs/authentication/
    '''
    try:
        df_keys_pressed = pd.read_sql_query(f'select distinct * from keys_pressed', con)
        df_clean_games_settings = pd.read_sql_query(f'select distinct * from clean_games_settings', con)
        df_summary_per_game = pd.read_sql_query(f'select distinct * from summary_per_game', con)
        df_clean_games_settings['capitalized_letters_count_perc'] = df_clean_games_settings['capitalized_letters_count_perc'].astype(str)
        # print(df_clean_games_settings)
        # print(pd.read_gbq('select * from pyfasttype.clean_games_settings'))
        df_clean_games_settings.to_gbq('pyfasttype.clean_games_settings', if_exists='replace', progress_bar=None)
        # print('clean_games_settings done')
        df_keys_pressed.to_gbq('pyfasttype.keys_pressed', if_exists='replace', progress_bar=None)
        # print('keys_pressed done')
        df_summary_per_game.to_gbq('pyfasttype.summary_per_game', if_exists='replace', progress_bar=None)
        print('Data pushed to GBQ')
    
    except Exception as error: 
        print("Error trying to push the data to GBQ. See errror below.")
        print(error)





clean_games_settings()
log_summary_per_game()


# # print(pd.read_sql_query('select * from summary_per_game', con).columns)




# push_to_gbq()