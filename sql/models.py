# -*- coding: UTF-8 -*-
from django.db import models
from django.contrib.auth.models import AbstractUser
from common.utils.aes_decryptor import Prpcrypt
from django.utils.translation import gettext as _


class ResourceGroup(models.Model):
    """
    资源组
    """
    group_id = models.AutoField('组ID', primary_key=True)
    group_name = models.CharField('组名称', max_length=100, unique=True)
    group_parent_id = models.BigIntegerField('父级id', default=0)
    group_sort = models.IntegerField('排序', default=1)
    group_level = models.IntegerField('层级', default=1)
    ding_webhook = models.CharField('钉钉webhook地址', max_length=255, blank=True)
    is_deleted = models.IntegerField('是否删除', choices=((0, '否'), (1, '是')), default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.group_name

    class Meta:
        managed = True
        db_table = 'resource_group'
        verbose_name = u'资源组管理'
        verbose_name_plural = u'资源组管理'


class Users(AbstractUser):
    """
    用户信息扩展
    """
    display = models.CharField('显示的中文名', max_length=50, default='')
    resource_group = models.ManyToManyField(ResourceGroup, related_name='res_group_users', help_text='资源组')
    ding_user_id = models.CharField('钉钉UserID', max_length=50, blank=True, null=True)
    failed_login_count = models.IntegerField('失败计数', default=0)
    last_login_failed_at = models.DateTimeField('上次失败登录时间', blank=True, null=True)

    def __str__(self):
        if self.display:
            return self.display
        return self.username

    class Meta:
        managed = True
        db_table = 'sql_users'
        verbose_name = u'用户管理'
        verbose_name_plural = u'用户管理'


class Tag(models.Model):
    """实例标签配置"""
    tag_code = models.CharField('标签代码', max_length=20, unique=True)
    tag_name = models.CharField('标签名称', max_length=20, unique=True)
    active = models.BooleanField('激活状态', default=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    def __str__(self):
        return self.tag_name

    class Meta:
        managed = True
        db_table = 'sql_tag'
        verbose_name = u'实例标签'
        verbose_name_plural = u'实例标签'


DB_TYPE_CHOICES = (
    ('mysql', 'MySQL'),
    ('mssql', 'MsSQL'),
    ('redis', 'Redis'),
    ('pgsql', 'PgSQL'),
    ('oracle', 'Oracle'),
    ('inception', 'Inception'),
    ('goinception', 'goInception'))


class Instance(models.Model):
    """
    各个线上实例配置
    """
    instance_name = models.CharField('实例名称', max_length=50, unique=True)
    type = models.CharField('实例类型', max_length=6, choices=(('master', '主库'), ('slave', '从库')))
    db_type = models.CharField('数据库类型', max_length=20, choices=DB_TYPE_CHOICES)
    host = models.CharField('实例连接', max_length=200)
    port = models.IntegerField('端口', default=0)
    user = models.CharField('用户名', max_length=100, default='', blank=True)
    password = models.CharField('密码', max_length=300, default='', blank=True)
    charset = models.CharField('字符集', max_length=20, default='', blank=True)
    service_name = models.CharField('Oracle service name', max_length=50, null=True, blank=True)
    sid = models.CharField('Oracle sid', max_length=50, null=True, blank=True)
    parent = models.ManyToManyField("self", symmetrical=False, related_name="children", blank=True)
    resource_group = models.ManyToManyField(ResourceGroup, related_name='res_group_instances', help_text='资源组')
    tag = models.ManyToManyField(Tag, related_name='instance', help_text='标签')
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    @property
    def raw_password(self):
        """ 返回明文密码 str """
        pc = Prpcrypt()  # 初始化
        return pc.decrypt(self.password)

    def __str__(self):
        return self.instance_name

    class Meta:
        managed = True
        db_table = 'sql_instance'
        # unique_together = ('host', 'port')
        verbose_name = u'实例配置'
        verbose_name_plural = u'实例配置'

    def save(self, *args, **kwargs):
        pc = Prpcrypt()  # 初始化
        if self.password:
            if self.id:
                old_password = Instance.objects.get(id=self.id).password
            else:
                old_password = ''
            # 密码有变动才再次加密保存
            self.password = pc.encrypt(self.password) if old_password != self.password else self.password
        super(Instance, self).save(*args, **kwargs)


class InstancePerf(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    base_path = models.CharField('Mysql BaseDir路径', max_length=50, default='/usr')
    conf_path = models.CharField('Mysql 配置文件路径', max_length=50, default='/etc/my.cnf')
    data_path = models.CharField('Mysql 数据目录', max_length=50, default='/var/lib/mysql')
    err_log_path = models.CharField('Mysql 错误日志目录', max_length=50, default='/var/lib/mysql')
    slow_log_path = models.CharField('Mysql 慢日志目录', max_length=50, default='/var/lib/mysql')
    disk_used = models.CharField('磁盘使用率', max_length=50, default='')
    disk_io = models.CharField('I/O速率', max_length=50, default="W:-1 K/s, R:-1 K/s")
    com_select = models.IntegerField('Query数', null=True, blank=True)
    threads_connected = models.IntegerField('总连接数', null=True, blank=True)
    threads_running = models.IntegerField('活跃会话数', null=True, blank=True)
    qps = models.FloatField('每秒增删改查量', null=True, blank=True)
    tps = models.IntegerField('每秒的事务量', null=True, blank=True)
    io = models.IntegerField('数据库I/O', null=True, blank=True)
    slow_queries = models.IntegerField('慢查询数', null=True, blank=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        managed = True
        db_table = 'sql_instance_perf'
        verbose_name = u'实例性能监控指标'
        verbose_name_plural = u'实例性能监控指标'


SQL_WORKFLOW_CHOICES = (
    ('workflow_finish', _('workflow_finish')),
    ('workflow_abort', _('workflow_abort')),
    ('workflow_manreviewing', _('workflow_manreviewing')),
    ('workflow_review_pass', _('workflow_review_pass')),
    ('workflow_timingtask', _('workflow_timingtask')),
    ('workflow_executing', _('workflow_executing')),
    ('workflow_autoreviewwrong', _('workflow_autoreviewwrong')),
    ('workflow_exception', _('workflow_exception')))


class SqlWorkflow(models.Model):
    """
    存放各个SQL上线工单的基础内容
    """
    workflow_name = models.CharField('工单内容', max_length=50)
    group_id = models.IntegerField('组ID')
    group_name = models.CharField('组名称', max_length=100)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    db_name = models.CharField('数据库', max_length=64)
    syntax_type = models.IntegerField('工单类型 0、未知，1、DDL，2、DML', choices=((0, '其他'), (1, 'DDL'), (2, 'DML')), default=0)
    is_backup = models.BooleanField('是否备份', choices=((False, '否'), (True, '是'),), default=True)
    engineer = models.CharField('发起人', max_length=30)
    engineer_display = models.CharField('发起人中文名', max_length=50, default='')
    status = models.CharField(max_length=50, choices=SQL_WORKFLOW_CHOICES)
    audit_auth_groups = models.CharField('审批权限组列表', max_length=255)
    run_date_start = models.DateTimeField('可执行起始时间', null=True, blank=True)
    run_date_end = models.DateTimeField('可执行结束时间', null=True, blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    finish_time = models.DateTimeField('结束时间', null=True, blank=True)
    is_manual = models.IntegerField('是否原生执行', choices=((0, '否'), (1, '是')), default=0)

    def __str__(self):
        return self.workflow_name

    class Meta:
        managed = True
        db_table = 'sql_workflow'
        verbose_name = u'SQL工单'
        verbose_name_plural = u'SQL工单'


class SqlWorkflowContent(models.Model):
    """
    存放各个SQL上线工单的SQL|审核|执行内容
    可定期归档或清理历史数据，也可通过``alter table sql_workflow_content row_format=compressed; ``来进行压缩
    """
    workflow = models.OneToOneField(SqlWorkflow, on_delete=models.CASCADE)
    sql_content = models.TextField('具体sql内容')
    review_content = models.TextField('自动审核内容的JSON格式')
    execute_result = models.TextField('执行结果的JSON格式', blank=True)

    def __str__(self):
        return self.workflow.workflow_name

    class Meta:
        managed = True
        db_table = 'sql_workflow_content'
        verbose_name = u'SQL工单内容'
        verbose_name_plural = u'SQL工单内容'


workflow_type_choices = ((1, _('sql_query')), (2, _('sql_review')))
workflow_status_choices = ((0, '待审核'), (1, '审核通过'), (2, '审核不通过'), (3, '审核取消'))


class WorkflowAudit(models.Model):
    """
    工作流审核状态表
    """
    audit_id = models.AutoField(primary_key=True)
    group_id = models.IntegerField('组ID')
    group_name = models.CharField('组名称', max_length=100)
    workflow_id = models.BigIntegerField('关联业务id')
    workflow_type = models.IntegerField('申请类型', choices=workflow_type_choices)
    workflow_title = models.CharField('申请标题', max_length=50)
    workflow_remark = models.CharField('申请备注', default='', max_length=140, blank=True)
    audit_auth_groups = models.CharField('审批权限组列表', max_length=255)
    current_audit = models.CharField('当前审批权限组', max_length=20)
    next_audit = models.CharField('下级审批权限组', max_length=20)
    current_status = models.IntegerField('审核状态', choices=workflow_status_choices)
    create_user = models.CharField('申请人', max_length=30)
    create_user_display = models.CharField('申请人中文名', max_length=50, default='')
    create_time = models.DateTimeField('申请时间', auto_now_add=True)
    sys_time = models.DateTimeField('系统时间', auto_now=True)

    def __int__(self):
        return self.audit_id

    class Meta:
        managed = True
        db_table = 'workflow_audit'
        unique_together = ('workflow_id', 'workflow_type')
        verbose_name = u'工作流审批列表'
        verbose_name_plural = u'工作流审批列表'


class WorkflowAuditDetail(models.Model):
    """
    审批明细表
    """
    audit_detail_id = models.AutoField(primary_key=True)
    audit_id = models.IntegerField('审核主表id')
    audit_user = models.CharField('审核人', max_length=30)
    audit_time = models.DateTimeField('审核时间')
    audit_status = models.IntegerField('审核状态', choices=workflow_status_choices)
    remark = models.CharField('审核备注', default='', max_length=140)
    sys_time = models.DateTimeField('系统时间', auto_now=True)

    def __int__(self):
        return self.audit_detail_id

    class Meta:
        managed = True
        db_table = 'workflow_audit_detail'
        verbose_name = u'工作流审批明细'
        verbose_name_plural = u'工作流审批明细'


class WorkflowAuditSetting(models.Model):
    """
    审批配置表
    """
    audit_setting_id = models.AutoField(primary_key=True)
    group_id = models.IntegerField('组ID')
    group_name = models.CharField('组名称', max_length=100)
    workflow_type = models.IntegerField('审批类型', choices=workflow_type_choices)
    audit_auth_groups = models.CharField('审批权限组列表', max_length=255)
    create_time = models.DateTimeField(auto_now_add=True)
    sys_time = models.DateTimeField(auto_now=True)

    def __int__(self):
        return self.audit_setting_id

    class Meta:
        managed = True
        db_table = 'workflow_audit_setting'
        unique_together = ('group_id', 'workflow_type')
        verbose_name = u'审批流程配置'
        verbose_name_plural = u'审批流程配置'


class WorkflowLog(models.Model):
    """
    工作流日志表
    """
    id = models.AutoField(primary_key=True)
    audit_id = models.IntegerField('工单审批id', db_index=True)
    operation_type = models.SmallIntegerField('操作类型，0提交/待审核、1审核通过、2审核不通过、3审核取消、4定时、5执行、6执行结束')
    operation_type_desc = models.CharField('操作类型描述', max_length=10)
    operation_info = models.CharField('操作信息', max_length=200)
    operator = models.CharField('操作人', max_length=30)
    operator_display = models.CharField('操作人中文名', max_length=50, default='')
    operation_time = models.DateTimeField(auto_now_add=True)

    def __int__(self):
        return self.audit_id

    class Meta:
        managed = True
        db_table = 'workflow_log'
        verbose_name = u'工作流日志'
        verbose_name_plural = u'工作流日志'


class QueryPrivilegesApply(models.Model):
    """
    查询权限申请记录表
    """
    apply_id = models.AutoField(primary_key=True)
    group_id = models.IntegerField('组ID')
    group_name = models.CharField('组名称', max_length=100)
    title = models.CharField('申请标题', max_length=50)
    # TODO user_name display 改为外键
    user_name = models.CharField('申请人', max_length=30)
    user_display = models.CharField('申请人中文名', max_length=50, default='')
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    db_list = models.TextField('数据库', default='')  # 逗号分隔的数据库列表
    table_list = models.TextField('表', default='')  # 逗号分隔的表列表
    valid_date = models.DateField('有效时间')
    limit_num = models.IntegerField('行数限制', default=100)
    priv_type = models.IntegerField('权限类型', choices=((1, 'DATABASE'), (2, 'TABLE'),), default=0)
    status = models.IntegerField('审核状态', choices=workflow_status_choices)
    audit_auth_groups = models.CharField('审批权限组列表', max_length=255)
    create_time = models.DateTimeField(auto_now_add=True)
    sys_time = models.DateTimeField(auto_now=True)

    def __int__(self):
        return self.apply_id

    class Meta:
        managed = True
        db_table = 'query_privileges_apply'
        verbose_name = u'查询权限申请记录表'
        verbose_name_plural = u'查询权限申请记录表'


class QueryPrivileges(models.Model):
    """
    用户权限关系表
    """
    privilege_id = models.AutoField(primary_key=True)
    user_name = models.CharField('用户名', max_length=30)
    user_display = models.CharField('申请人中文名', max_length=50, default='')
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    db_name = models.CharField('数据库', max_length=64, default='')
    table_name = models.CharField('表', max_length=64, default='')
    valid_date = models.DateField('有效时间')
    limit_num = models.IntegerField('行数限制', default=100)
    priv_type = models.IntegerField('权限类型', choices=((1, 'DATABASE'), (2, 'TABLE'),), default=0)
    is_deleted = models.IntegerField('是否删除', default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    sys_time = models.DateTimeField(auto_now=True)

    def __int__(self):
        return self.privilege_id

    class Meta:
        managed = True
        db_table = 'query_privileges'
        index_together = ["user_name", "instance", "db_name", "valid_date"]
        verbose_name = u'查询权限记录'
        verbose_name_plural = u'查询权限记录'


class QueryLog(models.Model):
    """
    记录在线查询sql的日志
    """
    # TODO 改为实例外键
    instance_name = models.CharField('实例名称', max_length=50)
    db_name = models.CharField('数据库名称', max_length=64)
    sqllog = models.TextField('执行的sql查询')
    effect_row = models.BigIntegerField('返回行数')
    cost_time = models.CharField('执行耗时', max_length=10, default='')
    # TODO 改为user 外键
    username = models.CharField('操作人', max_length=30)
    user_display = models.CharField('操作人中文名', max_length=50, default='')
    priv_check = models.BooleanField('查询权限是否正常校验', choices=((False, '跳过'), (True, '正常'),), default=False)
    hit_rule = models.BooleanField('查询是否命中脱敏规则', choices=((False, '未命中/未知'), (True, '命中')), default=False)
    masking = models.BooleanField('查询结果是否正常脱敏', choices=((False, '否'), (True, '是'),), default=False)
    create_time = models.DateTimeField('操作时间', auto_now_add=True)
    sys_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'query_log'
        verbose_name = u'查询日志'
        verbose_name_plural = u'查询日志'


class QueryExport(models.Model):
    query_log = models.ForeignKey(QueryLog, on_delete=models.CASCADE)
    auditor = models.ForeignKey(Users, on_delete=models.CASCADE)
    result_file = models.CharField('结果文件的存放路径', max_length=255, default='')
    error_msg = models.CharField('SQL执行错误信息', max_length=255, default='')
    reason = models.CharField('申请人导出数据原因', max_length=255, default='')
    audit_msg = models.CharField('审核人审核理由', max_length=255, default='')
    status = models.IntegerField('执行状态', choices=((0, '执行中'), (1, '执行失败'), (2, '待审核'),
                                                  (3, '审核通过'), (4, '审核不通过'), (5, '用户主动取消')))

    class Meta:
        db_table = 'query_export'
        verbose_name = u'导出查询表'
        verbose_name_plural = u'导出查询表'


class WPanHistory(models.Model):
    """
    用户将文件外传到微贷云盘的记录表
    """
    apply = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='upload_apply')
    auditor = models.ForeignKey(Users, null=True, blank=True, on_delete=models.SET_NULL, related_name='upload_auditor')
    file_path = models.CharField('文件路径', max_length=255, default='')
    reason = models.CharField('文件外传理由', max_length=255, default='')
    error_msg = models.TextField('外传错误信息', default='')
    audit_msg = models.CharField('审核人审核理由', max_length=255, default='')
    status = models.IntegerField('状态', choices=((0, '待审核'), (1, '审核通过'), (2, '审核不通过'),
                                                (3, '申请已过期'), (4, '用户主动取消'), (5, '上传失败')))
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'tools_wpan_history'
        verbose_name = u'工具：文件外传微贷云盘记录表'
        verbose_name_plural = u'工具：文件外传微贷云盘记录表'


# 脱敏字段配置
rule_type_choices = ((1, '手机号'), (2, '证件号码'), (3, '银行卡'), (4, '邮箱'), (5, '金额'), (6, '其他'))


class DataMaskingColumns(models.Model):
    """
    脱敏字段配置
    """
    column_id = models.AutoField('字段id', primary_key=True)
    rule_type = models.IntegerField('规则类型', choices=rule_type_choices)
    active = models.BooleanField('激活状态', choices=((False, '未激活'), (True, '激活')))
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    table_schema = models.CharField('字段所在库名', max_length=64)
    table_name = models.CharField('字段所在表名', max_length=64)
    column_name = models.CharField('字段名', max_length=64)
    column_comment = models.CharField('字段描述', max_length=1024, default='', blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    sys_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'data_masking_columns'
        verbose_name = u'脱敏字段配置'
        verbose_name_plural = u'脱敏字段配置'


class DataMaskingRules(models.Model):
    """
    脱敏规则配置
    """
    rule_type = models.IntegerField('规则类型', choices=rule_type_choices, unique=True)
    rule_regex = models.CharField('规则脱敏所用的正则表达式，表达式必须分组，隐藏的组会使用****代替', max_length=255)
    hide_group = models.IntegerField('需要隐藏的组')
    rule_desc = models.CharField('规则描述', max_length=100, default='', blank=True)
    sys_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'data_masking_rules'
        verbose_name = u'脱敏规则配置'
        verbose_name_plural = u'脱敏规则配置'


class ParamTemplate(models.Model):
    """
    实例参数模板配置
    """
    db_type = models.CharField('数据库类型', max_length=20, choices=DB_TYPE_CHOICES)
    variable_name = models.CharField('参数名', max_length=64)
    default_value = models.CharField('默认参数值', max_length=1024)
    editable = models.BooleanField('是否支持修改', default=False)
    valid_values = models.CharField('有效参数值，范围参数[1-65535]，值参数[ON|OFF]', max_length=1024, blank=True)
    description = models.CharField('参数描述', max_length=1024, blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    sys_time = models.DateTimeField('系统时间修改', auto_now=True)

    class Meta:
        managed = True
        db_table = 'param_template'
        unique_together = ('db_type', 'variable_name')
        verbose_name = u'实例参数模板配置'
        verbose_name_plural = u'实例参数模板配置'


class ParamHistory(models.Model):
    """
    可在线修改的动态参数配置
    """
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    variable_name = models.CharField('参数名', max_length=64)
    old_var = models.CharField('修改前参数值', max_length=1024)
    new_var = models.CharField('修改后参数值', max_length=1024)
    set_sql = models.CharField('在线变更配置执行的SQL语句', max_length=1024)
    user_name = models.CharField('修改人', max_length=30)
    user_display = models.CharField('修改人中文名', max_length=50)
    create_time = models.DateTimeField('参数被修改时间点', auto_now_add=True)

    class Meta:
        managed = True
        ordering = ['-create_time']
        db_table = 'param_history'
        verbose_name = u'实例参数修改历史'
        verbose_name_plural = u'实例参数修改历史'


class Config(models.Model):
    """
    配置信息表
    """
    item = models.CharField('配置项', max_length=50, primary_key=True)
    value = models.CharField('配置项值', max_length=200)
    description = models.CharField('描述', max_length=200, default='', blank=True)

    class Meta:
        managed = True
        db_table = 'sql_config'
        verbose_name = u'系统配置'
        verbose_name_plural = u'系统配置'


class AliyunAccessKey(models.Model):
    """
    记录阿里云的认证信息
    """
    ak = models.CharField(max_length=50)
    secret = models.CharField(max_length=100)
    is_enable = models.BooleanField('是否启用', default=True)
    remark = models.CharField(max_length=50, default='', blank=True)

    @property
    def raw_ak(self):
        """ 返回明文ak str """
        pc = Prpcrypt()  # 初始化
        return pc.decrypt(self.ak)

    @property
    def raw_secret(self):
        """ 返回明文secret str """
        pc = Prpcrypt()  # 初始化
        return pc.decrypt(self.secret)

    class Meta:
        managed = True
        db_table = 'aliyun_access_key'
        verbose_name = u'阿里云认证信息'
        verbose_name_plural = u'阿里云认证信息'

    def save(self, *args, **kwargs):
        pc = Prpcrypt()  # 初始化
        if self.id:
            old_info = AliyunAccessKey.objects.get(id=self.id)
            old_ak = old_info.ak
            old_secret = old_info.secret
        else:
            old_ak = ''
            old_secret = ''
        # 加密信息有变动才再次加密保存
        self.ak = pc.encrypt(self.ak) if old_ak != self.ak else self.ak
        self.secret = pc.encrypt(self.secret) if old_secret != self.secret else self.secret
        super(AliyunAccessKey, self).save(*args, **kwargs)


class AliyunRdsConfig(models.Model):
    """
    阿里云rds配置信息
    """
    instance = models.OneToOneField(Instance, on_delete=models.CASCADE)
    rds_dbinstanceid = models.CharField('对应阿里云RDS实例ID', max_length=100)
    is_enable = models.BooleanField('是否启用', default=True)

    def __int__(self):
        return self.rds_dbinstanceid

    class Meta:
        managed = True
        db_table = 'aliyun_rds_config'
        verbose_name = u'阿里云rds配置'
        verbose_name_plural = u'阿里云rds配置'


class Permission(models.Model):
    """
    自定义业务权限
    """

    class Meta:
        managed = True
        permissions = (
            ('menu_dashboard', '菜单 Dashboard'),
            ('menu_sqlcheck', '菜单 SQL审核'),
            ('menu_sqlworkflow', '菜单 SQL上线'),
            ('menu_sqlanalyze', '菜单 SQL分析'),
            ('menu_query', '菜单 SQL查询'),
            ('menu_sqlquery', '菜单 在线查询'),
            ('menu_query_export', '菜单 导出查询'),
            ('menu_queryapplylist', '菜单 权限管理'),
            ('menu_sqloptimize', '菜单 SQL优化'),
            ('menu_sqladvisor', '菜单 优化工具'),
            ('menu_slowquery', '菜单 慢查日志'),
            ('menu_backup', '菜单 备份'),
            ('menu_binlog', '菜单 Binlog管理'),
            ('menu_instance', '菜单 实例管理'),
            ('menu_instance_list', '菜单 实例列表'),
            ('instance_user', '实例用户查看'),
            ('instance_user_edit', '实例用户编辑'),
            ('menu_dbdiagnostic', '菜单 会话管理'),
            ('menu_database', '菜单 数据库管理'),
            ('menu_log', '菜单 日志管理'),
            ('menu_data_safe', '菜单 数据安全'),
            ('menu_host', '菜单 主机管理'),
            ('menu_param', '菜单 参数配置'),
            ('menu_data_dictionary', '菜单 数据字典'),
            ('menu_binlog2sql', '菜单 Binlog2SQL'),
            ('menu_schemasync', '菜单 SchemaSync'),
            ('menu_system', '菜单 系统管理'),
            ('menu_document', '菜单 相关文档'),
            ('menu_themis', '菜单 themis'),
            ('menu_tools', '菜单 高效小功能'),
            ('menu_wpan_upload', '菜单 上传微贷云盘'),
            ('wpan_upload_audit', '上传微贷云盘审核'),
            ('tools_loan_update', '订单所属业务员更改'),
            ('tools_loan_update_audit', '订单所属业务员更改审核'),
            ('sql_submit', '提交SQL上线工单'),
            ('sql_review', '审核SQL上线工单'),
            ('sql_execute_for_resource_group', '执行SQL上线工单(资源组粒度)'),
            ('sql_execute', '执行SQL上线工单(仅自己提交的)'),
            ('sql_analyze', '执行SQL分析'),
            ('optimize_sqladvisor', '执行SQLAdvisor'),
            ('optimize_sqltuning', '执行SQLTuning'),
            ('optimize_soar', '执行SOAR'),
            ('query_applypriv', '申请查询权限'),
            ('query_mgtpriv', '管理查询权限'),
            ('query_review', '审核查询权限'),
            ('query_export_review', '审核导出查询权限'),
            ('query_submit', '提交SQL查询'),
            ('query_all_instances', '可查询所有实例'),
            ('process_view', '查看会话'),
            ('database_edit', '编辑数据库'),
            ('binlog_del', '删除Binlog文件'),
            ('query_audit', '查询审计'),
            ('masking_field', '脱敏字段'),
            ('host', '物理主机管理'),
            ('process_kill', '终止会话'),
            ('tablespace_view', '查看表空间'),
            ('trxandlocks_view', '查看锁信息'),
            ('param_view', '查看实例参数列表'),
            ('param_edit', '修改实例参数'),
        )


class SlowQuery(models.Model):
    """
    SlowQuery
    """
    checksum = models.CharField(max_length=32, primary_key=True)
    fingerprint = models.TextField()
    sample = models.TextField()
    first_seen = models.DateTimeField(blank=True, null=True)
    last_seen = models.DateTimeField(blank=True, null=True, db_index=True)
    reviewed_by = models.CharField(max_length=20, blank=True, null=True)
    reviewed_on = models.DateTimeField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mysql_slow_query_review'
        verbose_name = u'慢日志统计'
        verbose_name_plural = u'慢日志统计'


class Replication(models.Model):
    master = models.CharField('主库实例名称', max_length=50)
    slave = models.CharField('从库实例名称', max_length=50)
    delay = models.IntegerField('Seconds_Behind_Master（主从延时）', blank=True, null=True)
    created = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        ordering = ("-created",)
        db_table = 'sql_replication'
        verbose_name = u'主从同步延时记录表'
        verbose_name_plural = u'主从同步延时记录表'


# Backup
class Backup(models.Model):
    bk_ip = models.CharField('备份服务器地址', max_length=15)
    db_cluster = models.CharField('实例名', max_length=32)
    db_type = models.CharField('数据库类型', max_length=15, null=True, blank=True)
    bk_type = models.CharField('备份类型', max_length=15, null=True, blank=True)
    bk_path = models.CharField('备份路径', max_length=32)
    bk_size = models.IntegerField()
    bk_state = models.SmallIntegerField()
    data_type = models.CharField('备份数据类型', max_length=6, choices=(('data', '数据'), ('binlog', 'Binlog')))
    check_man = models.CharField(max_length=15, default='DBA')
    bk_start_time = models.DateTimeField(blank=True, null=True)
    bk_end_time = models.DateTimeField(blank=True, null=True, db_index=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sql_backup'
        verbose_name = u'备份表'
        verbose_name_plural = u'备份表'


class QueryAudit(models.Model):
    query_time = models.DateTimeField('查询时间')
    instance_name = models.CharField('实例名', max_length=50)
    db_name = models.CharField('数据库名', max_length=20)
    db_user = models.CharField('数据库帐号', max_length=20)
    query_cost = models.FloatField('查询耗时')
    query_sql = models.TextField('查询语句')
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        ordering = ['-update_time']
        db_table = 'sql_query_audit'
        verbose_name = u'查询审计表'
        verbose_name_plural = u'查询审计表'


class Host(models.Model):
    os = models.CharField('系统版本', max_length=100)
    ip = models.CharField('IP地址', max_length=15)
    hostname = models.CharField('主机名', max_length=50)
    memory = models.CharField('内存', max_length=15)
    memory_used = models.FloatField('已用内存', null=True, blank=True)
    cpu = models.CharField('CPU', max_length=15)
    cpu_used = models.FloatField('已用CPU', null=True, blank=True)
    disk = models.TextField('硬盘', default='')
    net_io = models.CharField('网卡流量', max_length=50, null=True, blank=True)
    load_avg = models.CharField('负载', max_length=50)
    type = models.CharField(max_length=6, choices=(('master', 'Master'), ('slave', 'Slave')), default='master')
    inited = models.BooleanField('是否已经初始化环境', default=False)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        ordering = ['-update_time']
        db_table = 'sql_host'
        verbose_name = u'主机表'
        verbose_name_plural = u'主机表'


class DataBase(models.Model):
    host = models.ForeignKey(Host, on_delete=models.CASCADE, null=True, blank=True)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE, null=True, blank=True)
    instance_name = models.CharField('实例名', max_length=50, null=True, blank=True)
    db_name = models.CharField('数据库名', max_length=50, unique=True)
    app_type = models.CharField('业务分类', max_length=50, null=True, blank=True)
    db_application = models.CharField('用途', max_length=50)
    db_person = models.CharField('DB负责人', max_length=50)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        ordering = ['-update_time']
        db_table = 'sql_database'
        verbose_name = u'数据库表'
        verbose_name_plural = u'数据库表'


class BGTable(models.Model):
    db_name = models.CharField(max_length=50)
    table_name = models.CharField(max_length=50)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        ordering = ['db_name', 'table_name']
        unique_together = ('db_name', 'table_name')
        db_table = 'sql_bg_table'
        verbose_name = u'大数据抽取表'
        verbose_name_plural = u'大数据抽取表'


class ToolsLoanUpdate(models.Model):
    loan_id = models.CharField('订单编号', max_length=64)
    s_sale_id = models.CharField('原业务员账号', max_length=64, blank=True, null=True)
    s_sale_name = models.CharField('原业务员姓名', max_length=64, blank=True, null=True)
    t_sale_id = models.CharField('修正业务员账号', max_length=64, blank=True, null=True)
    t_sale_name = models.CharField('修正业务员姓名', max_length=64, blank=True, null=True)
    t_emp_id = models.CharField('修正业务员工号', max_length=64, blank=True, null=True)
    t_sale_uid = models.CharField('袋鼠uid', max_length=64, blank=True, null=True)
    t_pic_name = models.CharField('领导审批图片', max_length=255, default="")
    applicant = models.ForeignKey(Users, null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name='loan_update_apply')
    auditor = models.ForeignKey(Users, null=True, blank=True, on_delete=models.SET_NULL,
                                related_name='loan_update_auditor')
    audit_msg = models.CharField('审核理由', max_length=64, default="")
    status = models.SmallIntegerField('状态', choices=((0, '待审核'), (1, '审核通过'), (2, '审核不通过'),
                                                (3, '申请已过期'), (4, '用户主动取消')), default=0)
    update_time = models.DateTimeField('更新时间', auto_now=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        ordering = ("-update_time",)
        db_table = 't_loan_update'
        verbose_name = u'工具：订单修改'
        verbose_name_plural = u'工具：订单修改'


# SlowQueryHistory
class SlowQueryHistory(models.Model):
    """
    SlowQueryHistory
    """
    hostname_max = models.CharField(max_length=64, null=False)
    client_max = models.CharField(max_length=64, null=True)
    user_max = models.CharField(max_length=64, null=False)
    db_max = models.CharField(max_length=64, null=True, default=None)
    bytes_max = models.CharField(max_length=64, null=True)
    checksum = models.ForeignKey(SlowQuery, db_constraint=False, to_field='checksum', db_column='checksum',
                                 on_delete=models.CASCADE)
    sample = models.TextField()
    ts_min = models.DateTimeField(db_index=True)
    ts_max = models.DateTimeField()
    ts_cnt = models.FloatField(blank=True, null=True)
    query_time_sum = models.FloatField(db_column='Query_time_sum', blank=True, null=True)
    query_time_min = models.FloatField(db_column='Query_time_min', blank=True, null=True)
    query_time_max = models.FloatField(db_column='Query_time_max', blank=True, null=True)
    query_time_pct_95 = models.FloatField(db_column='Query_time_pct_95', blank=True, null=True)
    query_time_stddev = models.FloatField(db_column='Query_time_stddev', blank=True, null=True)
    query_time_median = models.FloatField(db_column='Query_time_median', blank=True, null=True)
    lock_time_sum = models.FloatField(db_column='Lock_time_sum', blank=True, null=True)
    lock_time_min = models.FloatField(db_column='Lock_time_min', blank=True, null=True)
    lock_time_max = models.FloatField(db_column='Lock_time_max', blank=True, null=True)
    lock_time_pct_95 = models.FloatField(db_column='Lock_time_pct_95', blank=True, null=True)
    lock_time_stddev = models.FloatField(db_column='Lock_time_stddev', blank=True, null=True)
    lock_time_median = models.FloatField(db_column='Lock_time_median', blank=True, null=True)
    rows_sent_sum = models.FloatField(db_column='Rows_sent_sum', blank=True, null=True)
    rows_sent_min = models.FloatField(db_column='Rows_sent_min', blank=True, null=True)
    rows_sent_max = models.FloatField(db_column='Rows_sent_max', blank=True, null=True)
    rows_sent_pct_95 = models.FloatField(db_column='Rows_sent_pct_95', blank=True, null=True)
    rows_sent_stddev = models.FloatField(db_column='Rows_sent_stddev', blank=True, null=True)
    rows_sent_median = models.FloatField(db_column='Rows_sent_median', blank=True, null=True)
    rows_examined_sum = models.FloatField(db_column='Rows_examined_sum', blank=True, null=True)
    rows_examined_min = models.FloatField(db_column='Rows_examined_min', blank=True, null=True)
    rows_examined_max = models.FloatField(db_column='Rows_examined_max', blank=True, null=True)
    rows_examined_pct_95 = models.FloatField(db_column='Rows_examined_pct_95', blank=True, null=True)
    rows_examined_stddev = models.FloatField(db_column='Rows_examined_stddev', blank=True, null=True)
    rows_examined_median = models.FloatField(db_column='Rows_examined_median', blank=True, null=True)
    rows_affected_sum = models.FloatField(db_column='Rows_affected_sum', blank=True, null=True)
    rows_affected_min = models.FloatField(db_column='Rows_affected_min', blank=True, null=True)
    rows_affected_max = models.FloatField(db_column='Rows_affected_max', blank=True, null=True)
    rows_affected_pct_95 = models.FloatField(db_column='Rows_affected_pct_95', blank=True, null=True)
    rows_affected_stddev = models.FloatField(db_column='Rows_affected_stddev', blank=True, null=True)
    rows_affected_median = models.FloatField(db_column='Rows_affected_median', blank=True, null=True)
    rows_read_sum = models.FloatField(db_column='Rows_read_sum', blank=True, null=True)
    rows_read_min = models.FloatField(db_column='Rows_read_min', blank=True, null=True)
    rows_read_max = models.FloatField(db_column='Rows_read_max', blank=True, null=True)
    rows_read_pct_95 = models.FloatField(db_column='Rows_read_pct_95', blank=True, null=True)
    rows_read_stddev = models.FloatField(db_column='Rows_read_stddev', blank=True, null=True)
    rows_read_median = models.FloatField(db_column='Rows_read_median', blank=True, null=True)
    merge_passes_sum = models.FloatField(db_column='Merge_passes_sum', blank=True, null=True)
    merge_passes_min = models.FloatField(db_column='Merge_passes_min', blank=True, null=True)
    merge_passes_max = models.FloatField(db_column='Merge_passes_max', blank=True, null=True)
    merge_passes_pct_95 = models.FloatField(db_column='Merge_passes_pct_95', blank=True, null=True)
    merge_passes_stddev = models.FloatField(db_column='Merge_passes_stddev', blank=True, null=True)
    merge_passes_median = models.FloatField(db_column='Merge_passes_median', blank=True, null=True)
    innodb_io_r_ops_min = models.FloatField(db_column='InnoDB_IO_r_ops_min', blank=True, null=True)
    innodb_io_r_ops_max = models.FloatField(db_column='InnoDB_IO_r_ops_max', blank=True, null=True)
    innodb_io_r_ops_pct_95 = models.FloatField(db_column='InnoDB_IO_r_ops_pct_95', blank=True, null=True)
    innodb_io_r_ops_stddev = models.FloatField(db_column='InnoDB_IO_r_ops_stddev', blank=True, null=True)
    innodb_io_r_ops_median = models.FloatField(db_column='InnoDB_IO_r_ops_median', blank=True, null=True)
    innodb_io_r_bytes_min = models.FloatField(db_column='InnoDB_IO_r_bytes_min', blank=True, null=True)
    innodb_io_r_bytes_max = models.FloatField(db_column='InnoDB_IO_r_bytes_max', blank=True, null=True)
    innodb_io_r_bytes_pct_95 = models.FloatField(db_column='InnoDB_IO_r_bytes_pct_95', blank=True, null=True)
    innodb_io_r_bytes_stddev = models.FloatField(db_column='InnoDB_IO_r_bytes_stddev', blank=True, null=True)
    innodb_io_r_bytes_median = models.FloatField(db_column='InnoDB_IO_r_bytes_median', blank=True, null=True)
    innodb_io_r_wait_min = models.FloatField(db_column='InnoDB_IO_r_wait_min', blank=True, null=True)
    innodb_io_r_wait_max = models.FloatField(db_column='InnoDB_IO_r_wait_max', blank=True, null=True)
    innodb_io_r_wait_pct_95 = models.FloatField(db_column='InnoDB_IO_r_wait_pct_95', blank=True, null=True)
    innodb_io_r_wait_stddev = models.FloatField(db_column='InnoDB_IO_r_wait_stddev', blank=True, null=True)
    innodb_io_r_wait_median = models.FloatField(db_column='InnoDB_IO_r_wait_median', blank=True, null=True)
    innodb_rec_lock_wait_min = models.FloatField(db_column='InnoDB_rec_lock_wait_min', blank=True, null=True)
    innodb_rec_lock_wait_max = models.FloatField(db_column='InnoDB_rec_lock_wait_max', blank=True, null=True)
    innodb_rec_lock_wait_pct_95 = models.FloatField(db_column='InnoDB_rec_lock_wait_pct_95', blank=True, null=True)
    innodb_rec_lock_wait_stddev = models.FloatField(db_column='InnoDB_rec_lock_wait_stddev', blank=True, null=True)
    innodb_rec_lock_wait_median = models.FloatField(db_column='InnoDB_rec_lock_wait_median', blank=True, null=True)
    innodb_queue_wait_min = models.FloatField(db_column='InnoDB_queue_wait_min', blank=True, null=True)
    innodb_queue_wait_max = models.FloatField(db_column='InnoDB_queue_wait_max', blank=True, null=True)
    innodb_queue_wait_pct_95 = models.FloatField(db_column='InnoDB_queue_wait_pct_95', blank=True, null=True)
    innodb_queue_wait_stddev = models.FloatField(db_column='InnoDB_queue_wait_stddev', blank=True, null=True)
    innodb_queue_wait_median = models.FloatField(db_column='InnoDB_queue_wait_median', blank=True, null=True)
    innodb_pages_distinct_min = models.FloatField(db_column='InnoDB_pages_distinct_min', blank=True, null=True)
    innodb_pages_distinct_max = models.FloatField(db_column='InnoDB_pages_distinct_max', blank=True, null=True)
    innodb_pages_distinct_pct_95 = models.FloatField(db_column='InnoDB_pages_distinct_pct_95', blank=True, null=True)
    innodb_pages_distinct_stddev = models.FloatField(db_column='InnoDB_pages_distinct_stddev', blank=True, null=True)
    innodb_pages_distinct_median = models.FloatField(db_column='InnoDB_pages_distinct_median', blank=True, null=True)
    qc_hit_cnt = models.FloatField(db_column='QC_Hit_cnt', blank=True, null=True)
    qc_hit_sum = models.FloatField(db_column='QC_Hit_sum', blank=True, null=True)
    full_scan_cnt = models.FloatField(db_column='Full_scan_cnt', blank=True, null=True)
    full_scan_sum = models.FloatField(db_column='Full_scan_sum', blank=True, null=True)
    full_join_cnt = models.FloatField(db_column='Full_join_cnt', blank=True, null=True)
    full_join_sum = models.FloatField(db_column='Full_join_sum', blank=True, null=True)
    tmp_table_cnt = models.FloatField(db_column='Tmp_table_cnt', blank=True, null=True)
    tmp_table_sum = models.FloatField(db_column='Tmp_table_sum', blank=True, null=True)
    tmp_table_on_disk_cnt = models.FloatField(db_column='Tmp_table_on_disk_cnt', blank=True, null=True)
    tmp_table_on_disk_sum = models.FloatField(db_column='Tmp_table_on_disk_sum', blank=True, null=True)
    filesort_cnt = models.FloatField(db_column='Filesort_cnt', blank=True, null=True)
    filesort_sum = models.FloatField(db_column='Filesort_sum', blank=True, null=True)
    filesort_on_disk_cnt = models.FloatField(db_column='Filesort_on_disk_cnt', blank=True, null=True)
    filesort_on_disk_sum = models.FloatField(db_column='Filesort_on_disk_sum', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mysql_slow_query_review_history'
        unique_together = ('checksum', 'ts_min', 'ts_max')
        index_together = ('hostname_max', 'ts_min')
        verbose_name = u'慢日志明细'
        verbose_name_plural = u'慢日志明细'
