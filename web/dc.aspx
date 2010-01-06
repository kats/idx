<%@ Page Language="C#" MasterPageFile="pfr.master" Inherits="Kontur.WebPFR.dcpage" AutoEventWireup="True" %>
<%@ Register TagPrefix="k" TagName="reportview" Src="reportview.ascx" %>
<%@ Register TagPrefix="k" TagName="ackview" Src="ackview.ascx" %>
<%@ Register TagPrefix="k" TagName="protocolview" Src="protocolview.ascx" %>
<asp:Content ContentPlaceHolderId="head" runat="server">
	<link rel="stylesheet" type="text/css" href="dc.css" media="screen">
</asp:Content>
<asp:Content ContentPlaceHolderId="content" runat="server">
	<div id="descr"><%=DescrStr()%></div>
	<div id="status" class="<%=StatusClass()%>">
		<%=StatusText()%>
	</div>
	<k:protocolview runat="server" id="protocolView" />
	<k:ackview runat="server" id="ackView" />
	<k:reportview runat="server" id="reportView" />
</asp:Content>
