<?php
define('MODEL_CACHE_LIFETIME', 120);
define('DEBUG', true);
define('IM_DOMAIN', 'http://test.im-ee.com/');
define('UPDATER_DOMAIN', 'https://updater.im-ee.com/');

//上传的临时目录
define('UPLOAD_TMP_DIR', ROOT . DS . 'cache' . DS . 'tmp' . DS);
define('UPLOAD_PIC_DIR', '/public/imgs/');
define('UPLOAD_PACKAGE_DIR', '/public/package/');

// android/ios下载地址
define('ANDROID_DOWNLOAD', 'http://ee-download.oss-cn-hangzhou.aliyuncs.com/ee_v1.0.0.7_release.apk');
define('IOS_DOWNLOAD', 'https://itunes.apple.com/app/apple-store/id1130768521?pt=118182784&mt=8');

define('Local_Server_Ip', '127.0.0.1');

define('GOOGLE_AUTH_CONFIG', APP_PATH . DS . 'libs' . DS . 'google-auth-config/api-8514658259142905394-467863-526729ee53f6.json');
define('GOOGLE_AUTH_CLIENT_EMAIL', 'test-pay@api-8514658259142905394-467863.iam.gserviceaccount.com');
define('PROXY_URL', 'http://47.244.191.22/proxy/');

define('Serv_Rpc_Gateway_Name', '127.0.0.1');
define('Serv_Learn_Proxy_Name', 'serv-learn-proxy.banban.private');
define('Serv_Im_Proxy_Name', 'serv-im-proxy.banban.private');

const CDN_IMG_DOMAIN = 'http://xs-image.yinjietd.com';
const CDN_IMG_PROXY_DOMAIN = 'http://xs-image-proxy.yinjietd.com';
const OSS_HOST = 'https://xs-image.oss-cn-hangzhou.aliyuncs.com';

return array(
	'db' => array(
        "host" => "mysql",
        "port" => 3306,
        "username" => "root",
        "password" => "123456",
        "dbname" => "xianshi",
        "charset" => 'utf8mb4'
    ),
    'banbandb' => array(
        "host" => "rm-bp1nfl3dp096d5o39.mysql.rds.aliyuncs.com",
        "port" => 3306,
        "username" => "normal",
        "password" => "dev123456",
        "dbname" => "banban",
        "charset" => 'utf8mb4'
    ),
	'activity' => array(
		"host" => "rm-bp1nfl3dp096d5o39.mysql.rds.aliyuncs.com",
		"port" => 3306,
		"username" => "super",
		"password" => "dev123456",
		"dbname" => "activity",
		"charset" => 'utf8mb4'
	),
    'proxy_db' => array(
        "host" => "rm-bp1nfl3dp096d5o39.mysql.rds.aliyuncs.com",
        "port" => 3306,
        "username" => "normal",
        "password" => "dev123456",
        "dbname" => "xianshi",
        "charset" => 'utf8mb4'
    ),
	'union_db' => array(
		"host" => "rm-bp1nfl3dp096d5o39.mysql.rds.aliyuncs.com",
		"port" => 3306,
		"username" => "super",
		"password" => "dev123456",
		"dbname" => "banban_union",
		"charset" => 'utf8mb4'
	),
    'readonly_db' => [
    array(
        "host" => "rm-bp1nfl3dp096d5o39.mysql.rds.aliyuncs.com",
        "port" => 3306,
        "username" => "normal",
        "password" => "dev123456",
        "dbname" => "xianshi",
        "charset" => 'utf8mb4'
    ),
    array(
        "host" => "rm-bp1nfl3dp096d5o39.mysql.rds.aliyuncs.com",
        "port" => 3306,
        "username" => "normal",
        "password" => "dev123456",
        "dbname" => "xianshi",
        "charset" => 'utf8mb4'
    ),
    array(
        "host" => "rm-bp1nfl3dp096d5o39.mysql.rds.aliyuncs.com",
        "port" => 3306,
        "username" => "normal",
        "password" => "dev123456",
        "dbname" => "xianshi",
        "charset" => 'utf8mb4'
    )
    ],

    'config_db' => [
        array(
            "host" => "rm-bp1nfl3dp096d5o39.mysql.rds.aliyuncs.com",
            "port" => 3306,
            "username" => "super",
            "password" => "dev123456",
            "dbname" => "config",
            "charset" => 'utf8mb4'
        ),
    ],
    'rush_db' => array(
        "host" => "rm-bp1nfl3dp096d5o39.mysql.rds.aliyuncs.com",
        "port" => 3306,
        "username" => "normal",
        "password" => "dev123456",
        "dbname" => "rush",
        "charset" => 'utf8mb4'
    ),
    'masterdb' => array(
        "host" => "rm-bp1nfl3dp096d5o39.mysql.rds.aliyuncs.com",
        "port" => 3306,
        "username" => "normal",
        "password" => "dev123456",
        "dbname" => "xianshi",
        "charset" => 'utf8mb4'
    ),
    'xssdb' => array(
        "host" => "rm-bp1nfl3dp096d5o39.mysql.rds.aliyuncs.com",
        "port" => 3306,
        "username" => "normal",
        "password" => "dev123456",
        "dbname" => "xss",
        "charset" => 'utf8mb4'
    ),
	'redis' => array(
		'host' => '127.0.0.1',
		'port' => 6379,
		'persistent' => false
	),
	'redis_old' => array(
		'host' => '127.0.0.1',
		'port' => 6379,
		'persistent' => false
	),
	'redis_es' => array(
		'host' => '127.0.0.1',
		'port' => 6379,
		'persistent' => false
	),
	'redis_user' => array(
		'host' => '127.0.0.1',
		'port' => 6379,
		'persistent' => false
	),
	'redis_room' => array(
		'host' => '127.0.0.1',
		'port' => 6378,
		'persistent' => false
	),
	'redis_record' => array(
		'host' => '127.0.0.1',
		'port' => 6379,
		'persistent' => false
	),
	'redis_mate' => array(
		'host' => '127.0.0.1',
		'port' => 6379,
		'persistent' => false
	),
	'redis_rpc' => array(
		'host' => '127.0.0.1',
		'port' => 6379,
		'persistent' => false
	),
	'beanstalk' => array(
		'host' => '127.0.0.1',
		'port' => 11300,
		'timeout' => 1
	),
	'redis_local' => array(
		'host' => '127.0.0.1',
		'port' => 6379,
		'persistent' => false,
	),
	'sphinx' => array(
		'host' => '127.0.0.1',
		'port' => 9312,
		'charset' => 'utf8'
	),
	'sphinx_all' => array(
		array(
			'host' => '127.0.0.1',
			'port' => 9312,
			'charset' => 'utf8'
		),
	),
	'lookup' => "172.16.0.87:4161",
	'nsq' => array(
#		"192.168.2.128:4160",
		"172.16.0.87:4150",
	),
	'nsq_circle' => array(
		"172.16.0.87:4150",
	),
	'nsq_room' => array(
		"172.16.0.87:4150",
	),
	'user_promote_active' => array(
		array(
			'host' => "http://127.0.0.1:9200",
			'username' => '',
			'password' => '',
		)
	),
	'es_new' => array(
		array(
			'host' => "http://127.0.0.1:9200",
			'username' => '',
			'password' => '',
		)
	),
	'es_vpc' => array(
		array(
			'host' => "http://127.0.0.1:9200",
			'username' => '',
			'password' => '',
		)
	),
	'rush_es' => array(
		array(
			'host' => "http://127.0.0.1:9200",
			'username' => '',
			'password' => '',
		)
	),
	/*
		cache 系统会将输出的http body缓存到xcache，并输出http header cache
		login true 系统会判断用户有没有登录，没有登录的会被定向到登录页面
		session true 系统会自动启用session，也可以自行在控制器中开启
		ui true 特殊用途，系统会将http body自动转化为javascript格式输出
	*/
	'map' => array(
		'account' => array(
			'sync' => array('login' => true),
			'profile' => array('login' => true),
			'money' => array('login' => true),
			'moneyLogRemove' => array('login' => true),
			'getUserInfo' => array('session' => true)
		),
		'cloud' => array(
			'token' => array('login' => true),
		),
		'upload' => array(
			'image' => array('login' => true),
		),
		'qq' => array(
			'oauthCallback' => array('session' => true),
			'index' => array('session' => true),
			'login' => array('session' => true),
			'logout' => array('session' => true),
		),
		'h5user' => array(
			'sendVerifyCodeImg' => array('session' => true),
			'sendVerifyCode' => array('session' => true),
//			'login' => array('session' => true),
			'loginuserprofile' => array('session' => true),
			'money' => array('login' => true),
			'bankcashvalid' => array('login' => true),
			'pbankcash' => array('login' => true),
			'pbankcash2' => array('login' => true),
			'cash' => array('login' => true),
			'bankcash' => array('login' => true),
			'idcard' => array('login' => true),
			'idcardset' => array('login' => true),
			'bankcard' => array('login' => true),
			'bankcardset' => array('login' => true),
			'spokesman' => array('login' => true),
			'spokesmanset' => array('login' => true),
			'spokesmaninfo' => array('login' => true),
			'agreeGodLicense' => array('login' => true),
		),
		'guest' => array(
			'visit' => array('login' => true),
			'visitor' => array('login' => true),
			'visible' => array('login' => true),
			'record' => array('login' => true),
			'list' => array('login' => true),
			'new' => array('login' => true),
			'stats' => array('login' => true),
			'delete' => array('login' => true),
			'clear' => array('login' => true),
		),
	
		'sleep' => array(
			'play' => array('login' => true),
			'thumbsUp' => array('login' => true),
		),
		'games/title'=>array(
			'index' => array('login' => true),
			'getGrowth' => array('login' => true),
		),
	),
	//这个define里的东西可以直接在模板里通过cfg使用
	'define' => array(
		//图片加载域
		'img' => 'http://img.imee.com/',
		'domain' => '/',
	),
);
