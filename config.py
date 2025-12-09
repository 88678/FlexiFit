#用於連接資料庫?
import os

class Config: 
    # 範例1：用 SQL Server 帳密登入（最常見）
    SQLALCHEMY_DATABASE_URI = "mssql+pyodbc://sa:jonsoncC7@localhost/FlexiFitDB?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
    SQLALCHEMY_TRACK_MODIFICATIONS = False     # 關閉追蹤修改警告（節省記憶體）
    SECRET_KEY = '期末作業隨便打' # 密鑰（用於 session 加密，生產環境請改用環境變數）
    
    # JSON_AS_ASCII = False # JSON 支援中文 讓中文正常顯示。Flask 2.3 版本以後，這個設定參數已被移除並棄用
        