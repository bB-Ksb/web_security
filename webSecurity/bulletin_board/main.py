from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import pymysql

app = FastAPI()

# 데이터베이스 설정
db_config = {
    'host': 'database_link', ## 보안문제로 데이터베이스 링크는 가린 채 올립니다
    'port': 3306,
    'user': 'admin',
    'password': '', ## 보안 문제로 데이터베이스 비밀번호는 가린채 올립니다
    'database': 'database-1',
    'charset': 'utf8mb4'
}


# 데이터베이스 커서 설정
def get_connection():
    return pymysql.connect(**db_config)


# 게시판 루트 페이지 엔드포인트
@app.get("/", response_class=HTMLResponse)
async def read_root():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT username, title, content, created_at FROM posts"
            cursor.execute(sql)
            results = cursor.fetchall()
    finally:
        conn.close()

    posts_html = ""
    for username, title, content, created_at in results:
        posts_html += f"""
            <tr class='body'>
                <td>{username}</td>
                <td class='title'>{title}</td>
                <td>{content}</td>
                <td>{created_at.strftime("%Y-%m-%d %H:%M:%S")}</td>
            </tr>
        """

    with open("templates/index.html", "r", encoding="utf-8") as file:
        html_content = file.read()

    html_content = html_content.replace("{{ posts }}", posts_html)

    return HTMLResponse(content=html_content)


# 글쓰기 페이지 엔드포인트
@app.get("/write", response_class=HTMLResponse)
async def write_post():
    with open("templates/write.html", "r", encoding="utf-8") as file:
        html_content = file.read()

    return HTMLResponse(content=html_content)


# 게시글 생성 엔드포인트
@app.post("/posts/", response_class=HTMLResponse)
async def create_post(username: str = Form(...), title: str = Form(...), content: str = Form(...)):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO posts (username, title, content) VALUES (%s, %s, %s)"
            cursor.execute(sql, (username, title, content))
        conn.commit()
    finally:
        conn.close()

    return RedirectResponse(url="/", status_code=303)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
