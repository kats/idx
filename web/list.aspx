<%@ Page Language="C#" CodeFile="list.aspx.cs" Inherits="Kontur.WebPFR.list" MasterPageFile="pfr.master" AutoEventWireup="True" %>
<asp:Content ContentPlaceHolderId="content" runat="server">
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
</asp:Content>
