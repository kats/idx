<%@ Page Language="C#" MasterPageFile="pfr.master" CodeFile="dc.aspx.cs" Inherits="Kontur.WebPFR.dcpage" AutoEventWireup="True" %>
<asp:Content ContentPlaceHolderId="content" runat="server">
	<div id="descr"><%=DescrStr()%></div>
	<div id="status" class="<%=StatusClass()%>">
		<%=StatusText()%>
	</div>
</asp:Content>
