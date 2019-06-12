from flask import Flask, render_template, request, json, redirect, url_for, send_from_directory, abort, jsonify, \
    flash, session, logging, send_file
from py2neo import Graph, Node, Relationship, NodeMatcher
from py2neo.matching import RelationshipMatcher

app = Flask(__name__)
graph = Graph("http://localhost:7474", username="neo4j", password='123')


# 首页渲染
@app.route('/')
def main():
    return render_template('neo4j.html')


# 用户id查询页渲染
@app.route('/show')
def show():
    return render_template('show.html')


# 用户id查询
@app.route('/')
def searchUserId(id):
    node_for_userid = Node("neo4j_ratings", name=id)
    graph.create(node_for_userid)
    dict_user_movie = {}
    result = []
    find_user_node = graph.run("match (n:neo4j_ratings{userId:'" + id + "'}) return n")
    for i in find_user_node:
        dict_user_movie.update(dict(i['n']))
        result.append(dict(i['n']))

    for i in result:
        temp = i["timestamp"]
        i["timestamp"] = int(temp)

    result.sort(key=lambda k: k['timestamp'])

    count = 0
    for i in result:
        print(i)
        forEachMovieId = i["movieId"]
        find_movie_tags = graph.run("match (n:neo4j_tags{movieId:'" + forEachMovieId + "'}) return n")
        find_movie_title = graph.run("match(n:neo4j_movies{movieId:'" + forEachMovieId + "'})return n")

        for r in find_movie_title:
            print("movie'title:" + r['n']['title'])
            i['movieTitle'] = r['n']['title']

        i['tags'] = []
        for j in find_movie_tags:
            count = count + 1
            if count <= 3:
                print(j['n']['tag'])
                i['tags'].append(j['n']['tag'])
                forEachtagName = j['n']['tag']
                find_tag_tagIds = graph.run("match (n:neo4j_genometags{tag:'" + forEachtagName + "'}) return n")
                for k in find_tag_tagIds:
                    theTagId = k['n']['tagId']
                    relevance = graph.run(
                        "MATCH (na:neo4j_movies{movieId:'" + forEachMovieId + "'})-[r:re]->(nb:neo4j_genometags{tagId:'" + theTagId + "'}) RETURN r")
                    for m in relevance:
                        print("relevance:" + m)
                        print("")

            else:
                count = 0
                break

    print(" ")
    print(result)
    return result


# 关键字查询
@app.route('/')
def searchKeywords(movieName):
    result = []
    matcher = NodeMatcher(graph)

    find_movie_node = graph.run(" match(n:neo4j_movies) where n.title =~'.*" + movieName + ".*' return n ")
    for i in find_movie_node:
        print(dict(i['n']))
        result.append(dict(i['n']))
    return result


# 风格查询
@app.route('/')
def searchStyle(s):
    result = []
    find_movie_node = graph.run(" match(n:neo4j_movies) where n.title =~'.*" + movieName + ".*' return n ")
    for i in find_movie_node:
        print(dict(i['n']))
        result.append(dict(i['n']))
    return result


# 输入查询条件
@app.route('/', methods=['POST'])
def toSearch():
    _searchCondition = request.form['search-condition']
    _querySelect = request.form['query-select']
    if _querySelect == 'user-id':
        return redirect(url_for('showUserId', user_id=_searchCondition))
    elif _querySelect == 'key-words':
        # 调用关键字查询的函数
        return redirect(url_for('showMovie', keyWords=_searchCondition))
    elif _querySelect == 'style':
        # 调用风格查询的函数
        searchStyle(_searchCondition)
    return render_template('neo4j.html')


# 用户id查询页渲染
@app.route('/showUserId/<user_id>', methods=['GET'])
def showUserId(user_id):
    result = searchUserId(user_id)
    return render_template('show.html', id=user_id, list=result)


# 电影关键字查询页渲染
@app.route('/showMovie/<keyWords>', methods=['GET'])
def showMovie(keyWords):
    result = searchKeywords(keyWords)
    return render_template('showMovie.html', key=keyWords, list=result)


@app.route('showMovie/<style>', methods=['GET'])
def showStyle(style):
    result = searchStyle(style)
    return render_template("showStyle.html", style=style, list=result)


if __name__ == '__main__':
    app.run(debug=True)