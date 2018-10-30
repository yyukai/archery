# -*- coding: UTF-8 -*- 

from django.urls import path

from common import auth, config, workflow, dashboard, check
from sql import views, sql_workflow, query, slowlog, instance, db_diagnostic, sql_tuning, group, \
    sql_advisor, binlog2sql, backup, binlog, data_safe, query_audit, ip_white, host
from sql.utils import jobs

urlpatterns = [
    path('', views.sqlworkflow),
    path('index/', views.sqlworkflow),
    path('login/', views.login, name='login'),
    path('logout/', auth.sign_out),
    path('signup/', auth.sign_up),
    path('sqlworkflow/', views.sqlworkflow),
    path('submitsql/', views.submitSql),
    path('editsql/', views.submitSql),
    path('submitotherinstance/', views.submitSql),
    path('detail/<int:workflowId>/', views.detail, name='detail'),
    path('autoreview/', sql_workflow.autoreview),
    path('passed/', sql_workflow.passed),
    path('execute/', sql_workflow.execute),
    path('timingtask/', sql_workflow.timingtask),
    path('cancel/', sql_workflow.cancel),
    path('rollback/', views.rollback),
    path('sqlquery/', views.sqlquery),
    path('query_export/', views.query_export),
    path('slowquery/', views.slowquery),
    path('sqladvisor/', views.sqladvisor),
    path('slowquery_advisor/', views.sqladvisor),
    path('queryapplylist/', views.queryapplylist),
    path('queryapplydetail/<int:apply_id>/', views.queryapplydetail, name='queryapplydetail'),
    path('queryuserprivileges/', views.queryuserprivileges),
    path('dbdiagnostic/', views.dbdiagnostic),
    path('workflow/', views.workflows),
    path('workflow/<int:audit_id>/', views.workflowsdetail),
    path('dbaprinciples/', views.dbaprinciples),
    path('dashboard/', dashboard.pyecharts),
    path('group/', views.group),
    path('grouprelations/<int:group_id>/', views.groupmgmt),
    path('instance/', views.instance),
    path('instanceuser/<int:instance_id>/', views.instanceuser),
    path('binlog2sql/', views.binlog2sql),
    path('schemasync/', views.schemasync),
    path('config/', views.config),

    path('authenticate/', auth.authenticateEntry),
    path('sqlworkflowlist/', sql_workflow.sqlworkflowlist),
    path('simplecheck/', sql_workflow.simplecheck),
    path('getOscPercent/', sql_workflow.getOscPercent),
    path('getWorkflowStatus/', sql_workflow.getWorkflowStatus),
    path('stopOscProgress/', sql_workflow.stopOscProgress),
    path('del_sqlcronjob/', jobs.del_sqlcronjob),

    path('workflow/list/', workflow.lists),
    path('workflow/log/', workflow.log),
    path('config/change/', config.changeconfig),

    path('check/inception/', check.inception),
    path('check/email/', check.email),
    path('check/instance/', check.instance),

    path('group/group/', group.group),
    path('group/addrelation/', group.addrelation),
    path('group/relations/', group.associated_objects),
    path('group/instances/', group.instances),
    path('group/unassociated/', group.unassociated_objects),
    path('group/auditors/', group.auditors),
    path('group/changeauditors/', group.changeauditors),

    path('instance/list/', instance.lists),
    path('instance/users/', instance.users),
    path('instance/schemasync/', instance.schemasync),
    path('instance/getdbNameList/', instance.getdbNameList),
    path('instance/getTableNameList/', instance.getTableNameList),
    path('instance/getColumnNameList/', instance.getColumnNameList),

    path('database/', views.database),
    path('database/list/', instance.db_list),

    path('replication/', views.replication),
    path('replication_delay/', instance.replication_delay),
    path('replication_echart/', views.replication_echart),

    path('param/', views.param),
    path('param/list/', instance.param_list),
    path('param/history/', instance.param_history),
    path('param/save/', instance.param_save),

    path('query/', query.query),
    path('add_async_query/', query.add_async_query),
    path('query_result_export/', query.query_result_export),
    path('query_export_audit/', query.query_export_audit),
    path('query/querylog/', query.querylog),
    path('query/query_export_log/', query.query_export_log),
    path('query/explain/', query.explain),
    path('query/applylist/', query.getqueryapplylist),
    path('query/userprivileges/', query.getuserprivileges),
    path('query/applyforprivileges/', query.applyforprivileges),
    path('query/modifyprivileges/', query.modifyqueryprivileges),
    path('query/privaudit/', query.queryprivaudit),

    path('binlog/', views.binlog),
    path('binlog/list/', binlog.binlog_list),
    path('binlog/delete_log/', binlog.delete_log),
    path('binlog2sql/sql/', binlog2sql.binlog2sql),
    path('binlog2sql/binlog_list/', binlog2sql.binlog_list),

    path('slowquery/review/', slowlog.slowquery_review),
    path('slowquery/review_history/', slowlog.slowquery_review_history),
    path('slowquery/sqladvisor/', sql_advisor.sqladvisorcheck),
    path('slowquery/sqltuning/', sql_tuning.tuning),

    path('db_diagnostic/process/', db_diagnostic.process),
    path('db_diagnostic/create_kill_session/', db_diagnostic.create_kill_session),
    path('db_diagnostic/kill_session/', db_diagnostic.kill_session),
    path('db_diagnostic/tablesapce/', db_diagnostic.tablesapce),
    path('db_diagnostic/trxandlocks/', db_diagnostic.trxandlocks),

    path('backup/', views.backup),
    path('backup/list/', backup.backup_list),
    path('backup_detail/<db_cluster>/', views.backup_detail),
    path('backup_detail/list/<db_cluster>/', backup.backup_detail_list),

    path('masking_field/', views.masking_field),
    path('masking_field/list/', data_safe.masking_field_list),

    path('query_audit/', views.query_audit),
    path('query_audit/list/', query_audit.query_audit),

    path('ip_white/<int:instance_id>/', views.ip_white),
    path('ip_white/list/<int:instance_id>', ip_white.ip_white_list),
    path('ip_white/add/<int:instance_id>', ip_white.ip_white_add),
    path('ip_white/edit/<int:instance_id>', ip_white.ip_white_add),
    path('ip_white/delete/<int:instance_id>', ip_white.ip_white_del),

    path('host/', views.host),
    path('host/list/', host.host_list),
]
