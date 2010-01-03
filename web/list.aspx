<%@ Page Language="C#" CodeFile="list.aspx.cs" Inherits="Kontur.WebPFR.list" AutoEventWireup="True" %>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
	<head>
		<link rel="stylesheet" type="text/css" href="tabs.css" media="screen">
		<link rel="stylesheet" type="text/css" href="list.css" media="screen">
	</head>
	<body>
		<div id="head">
			<span>ЗАО &laquo;Хороший дизайн&raquo;</span>
			<!--a href="#">Справка</a> -->
		</div>
		<ul id="tabs" class="tabs">
			<li class="active"><a>Отправленные</a>
			<li><a href="#">Отправить сведения &hellip;</a>
			<li><a href="#">Регистрационные данные</a>
		</ul>
		<table id="dcs" cellspacing="0" cellpadding="0">
			<thead>
				<tr><th class="status">Статус сведений</th><th>Сведения</th><th>УПФР</th><th>Дата</th></tr>
			</thead>
			<tbody>
				<%=GetRows()%>
			</tbody>
		</table>
		<div id="pages">
			<strong><%=PageCount%> <%=Word()%>:</strong>
			<div id="arrows">
				<%=PrevHref()%>
				<%=NextHref()%>
			</div>
		</div>
	</body>
</html>
