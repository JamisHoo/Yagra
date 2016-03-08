#Yagra

##功能及实现

###用户管理
1. 注册

    注册后服务器会发一封激活邮件，用户点击邮件中的激活链接后方可登录。

2. 重置密码
    
    服务器发送一封带有重置密码链接的邮件到用户邮箱，链接将在以下情况下失效：
    
    * 链接被使用
    * 15分钟后（可在配置文件中修改）
    * 用户请求重新发送重置密码的链接
    * 用户通过原密码登录成功

3. 登录及Cookie
    
    服务端保存每个用户独立的salt及密码的hash，计算方式为`hash=SHA-256(salt+plaintext)`，每次重置密码后更新salt。每次用户登录成功后，服务端生成一个随机的长密码作为Cookie，并在服务端保存该随机密码的hash。Cookie一段时间后失效，可在配置文件中设定失效时间。修改密码后Cookie亦失效。
    
###头像

每个用户可以上传一张图片作为头像，并为自己上传的头像选择评级（G、PG、R、X）。

访问的方式为`http://domain/HASH`。

其中HASH的计算方式与[Gravatar](http://en.gravatar.com/)略有不同。根据[RFC 5321](https://datatracker.ietf.org/doc/rfc5321/)规定，用户标识部分（即@前面的部分）可能是大小写敏感的。同时考虑到实现简便，HASH的计算方式为`HASH=MD5(trim(Email))`。

因图片剪裁功能要引入第三方库，访问图片时只能访问原始大小。

可以通过`d=`或`default=`参数指定图片不存在时的默认图片，支持`d=URL-encoded`、`d=404`、`d=blank`。

支持`f=`或`forcedefault=`强制返回默认图片；
支持`r=`或`rating=`指定允许显示的图片评级；
支持多个参数组合。
参数功能及使用方法均与[Gravatar](http://en.gravatar.com/)相同，不赘述。

##部署方式

以Apache HTTP Server为例。实际操作因平台而异，不必拘泥一格。

1. 安装Apache HTTP Server

2. 安装MySQL Server

3. 安装MySQL-python

4. 安装Postfix

5. 配置Apache HTTP Server
    
    把cgi-bin目录中的文件复制到适当的位置（例如`/var/www/cgi-bin/`）
    
    修改httpd.conf

    ```
    <IfModule alias_module>
        ScriptAliasMatch /[0-9A-Fa-f]{32}$ "/var/www/cgi-bin/request_image.py"
        ScriptAlias / "/var/www/cgi-bin/"
    </IfModule>
    ```
    
6. 配置MySQL Server
    
    运行以下命令

    ```
    CREATE DATABASE yagra;
    USE yagra;
    
    CREATE TABLE users (email VARCHAR(255) NOT NULL,
                        email_hash BINARY(16) NOT NULL,
                        salt BINARY(32) NOT NULL,
                        passwd_hash BINARY(32) NOT NULL,
                        random_passwd_hash BINARY(32),
                        image LONGBLOB,
                        rating VARCHAR(2),
                        reset_passwd_token BINARY(32),
                        reset_passwd_token_expires BIGINT,
                        activate_token BINARY(32),
                        PRIMARY KEY(email));
    
    CREATE INDEX reset_passwd_token_index ON users(reset_passwd_token);
    CREATE INDEX activate_token_index ON users(activate_token);
    ```
    
7. 配置config.py

    修改`cgi-bin/common/config.py`，文件内有注释，不在此赘述。
