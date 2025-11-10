import json
from .task import MBIOTask
from .xmlconfig import XMLConfig

from .wserver import TemporaryWebServer


class Html():
    def __init__(self, title=None):
        self._header=''
        self._body=''
        if title:
            self.header(f'<title>{title}</title>')

        self.header('<meta charset="utf-8" />')
        self.header('<meta name="viewport" content="width=device-width, initial-scale=1" />')

        # self.header('<link rel="stylesheet" href="/www/jquery-ui/jquery-ui.min.css">')
        # self.header('<script src="/www/jquery-ui/external/jquery/jquery.js"></script>')
        # self.header('<script src="/www/jquery-ui/jquery-ui.min.js"></script>')

        # https://jquery.com/download/
        self.body('<script src="/www/jquery/jquery.min.js"></script>')

        # https://getbootstrap.com/docs/5.0/getting-started/download/
        self.header('<link href="/www/Bootstrap/dist/css/bootstrap.min.css" rel="stylesheet">')
        self.body('<script src="/www/Bootstrap/dist/js/bootstrap.bundle.min.js"></script>')

        # https://datatables.net/download/
        self.header('<link href="/www/DataTables/datatables.min.css" rel="stylesheet">')
        self.body('<script src="/www/DataTables/datatables.min.js"></script>')

        self.style('.red-button {background-color: red; color: white;}')

        data="""
        .form-switch {
        position: relative;
        display: inline-block;
        width: 42px;
        height: 22px;
        }

        .form-switch input {
        opacity: 0;
        width: 0;
        height: 0;
        }

        .form-switch .slider {
        position: absolute;
        cursor: pointer;
        top: 0; left: 0; right: 0; bottom: 0;
        background-color: #ccc;
        border-radius: 22px;
        transition: .3s;
        }

        .form-switch .slider:before {
        position: absolute;
        content: "";
        height: 18px; width: 18px;
        left: 2px; bottom: 2px;
        background-color: white;
        border-radius: 50%;
        transition: .3s;
        }

        .form-switch input:checked + .slider {
        background-color: #4caf50;
        }

        .form-switch input:checked + .slider:before {
        transform: translateX(20px);
        }
        """
        self.style(data)

    def header(self, data):
        if data:
            self._header+=data
            self._header+='\n'

    def style(self, data):
        if data:
            self.header(f'<style>{data}</style>')

    def body(self, data):
        if data:
            self._body+=data
            self._body+='\n'

    def write(self, data):
        self.body(data)

    def data(self):
        data='<html>'
        data+='<head>'
        data+=self._header
        data+='</head>'
        data+='<body>'
        data+=self._body
        data+='</body>'
        data+='</html>'
        return data

    def bytes(self):
        return self.data().encode('utf-8')

    def button(self, bid, name):
        self.write(f'<button id="{bid}" class="ui-button red-button ui-widget ui-corner-all">{name}</button>')


class MBIOWsMonitor(MBIOTask):
    def initName(self):
        return 'wsmon'

    @property
    def wserver(self) -> TemporaryWebServer:
        return self._wserver

    def onInit(self):
        self._wserver=None

    def cb_mycallback(self, handler, params):
        handler.send_response(200)
        handler.send_header("Content-Type", "text/html; charset=utf-8")
        handler.end_headers()

        h=Html('MBIO Processor Monitor')
        # h.button('test', 'Let\'s GO!')

        mbio=self.getMBIO()
        for g in mbio.gateways.all():
            h.button(g.name, str(g))

        handler.wfile.write(h.bytes())

    def cb_headers_json(self, handler, rcode=200):
        handler.send_response(rcode)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.end_headers()

    def cb_write_json(self, handler, data, rcode=200):
        self.cb_headers_json(handler, rcode)
        data=json.dumps(data)
        handler.wfile.write(data.encode('utf-8'))

    def cb_write_success(self, handler):
        data={'success': True}
        return self.cb_write_json(handler, data)

    def cb_write_failure(self, handler):
        data={'success': False}
        return self.cb_write_json(handler, data, 400)

    def cb_gettasks(self, handler, params):
        mbio=self.getMBIO()
        items=[]
        for t in mbio.tasks.all():
            item={'key': t.key}
            item['class']=t.__class__.__name__
            item['state']=t.statestr(),
            item['statetime']=int(t.statetime())
            item['error']=t.isError()
            item['countvalues']=t.values.count()
            items.append(item)

        data={'data': items}
        self.cb_write_json(handler, data)
        return True

    def cb_resettask(self, handler, params):
        mbio=self.getMBIO()
        key=params.get('key')
        t=mbio.task(key)
        if t:
            t.reset()
            self.cb_write_success(handler)
            return True
        self.cb_write_failure(handler)

    def cb_resetgateway(self, handler, params):
        mbio=self.getMBIO()
        key=params.get('key')
        g=mbio.gateway(key)
        if g:
            g.reset()
            self.cb_write_success(handler)
            return True
        self.cb_write_failure(handler)

    def cb_resetdevice(self, handler, params):
        mbio=self.getMBIO()
        gateway=params.get('gateway')
        key=params.get('key')
        g=mbio.gateway(gateway)
        if g:
            d=g.device(key)
            if d:
                d.reset()
                self.cb_write_success(handler)
                return True
        self.cb_write_failure(handler)

    def cb_setvalue(self, handler, params):
        mbio=self.getMBIO()
        key=params.get('key')
        v=params.get('value')
        value=mbio.value(key)
        if value is not None:
            if v=="auto":
                value.auto()
            else:
                value.manual(v)
            self.cb_write_success(handler)
            return True
        self.cb_write_failure(handler)

    def cb_setvalueauto(self, handler, params):
        mbio=self.getMBIO()
        key=params.get('key')
        value=mbio.value(key)
        if value is not None:
            value.auto()
            self.cb_write_success(handler)
            return True
        self.cb_write_failure(handler)

    def cb_getgateways(self, handler, params):
        mbio=self.getMBIO()
        items=[]
        for g in mbio.gateways.all():
            item={'key': g.key, 'name': g.name, 'host': g.host, 'mac': g.MAC, 'model': g.model}
            item['class']=g.__class__.__name__
            state='CLOSED'
            if g.isOpen():
                state='OPEN'
            item['state']=state
            item['error']=g.isError()
            item['countdevices']=g.devices.count()
            items.append(item)

        data={'data': items}
        self.cb_write_json(handler, data)
        return True

    def cb_getgatewaydevices(self, handler, params):
        mbio=self.getMBIO()
        g=mbio.gateway(params.get('gateway'))

        items=[]
        if g is not None:
            for d in g.devices.all():
                self.microsleep()
                item={'gateway': g.key, 'address': d.address, 'key': d.key, 'vendor': d.vendor, 'model': d.model, 'state': d.statestr()}
                item['class']=d.__class__.__name__
                item['version']=d.version
                item['statetime']=int(d.statetime())
                item['countmsg']=d.countMsg
                item['countmsgerr']=d.countMsgErr
                item['error']=d.isError()
                item['countvalues']=d.values.count()
                item['ismanualvalue']=d.isManualValue()
                item['countvalues']=d.values.count()
                items.append(item)

        data={'data': items}
        self.cb_write_json(handler, data)
        return True

    def cb_gettaskvalues(self, handler, params):
        mbio=self.getMBIO()
        t=mbio.task(params.get('task'))

        items=[]
        if t is not None:
            for v in t.values.all():
                self.microsleep()
                if not v.isEnabled():
                    continue
                item={'key': v.key, 'value': v.value, 'toreachvalue': None,
                        'valuestr': v.valuestr(),
                        'unit': v.unit, 'unitstr': v.unitstr(),
                        'flags': v.flags, 'age': int(v.age()), 'tag': v.tag}
                if v.isWritable():
                    item['toreachvalue']=v.toReachValue
                item['class']=v.__class__.__name__
                item['error']=v.isError()
                item['writable']=v.isWritable()
                item['digital']=v.isDigital()
                item['enable']=v.isEnabled()
                item['manual']=v.isManual()
                item['description']=v.description
                items.append(item)

        data={'data': items}
        self.cb_write_json(handler, data)
        return True

    def cb_getdevicevalues(self, handler, params):
        mbio=self.getMBIO()
        g=mbio.gateway(params.get('gateway'))

        items=[]
        if g is not None:
            d=g.device(params.get('device'))
            if d is not None:
                for v in d.values.all():
                    self.microsleep()
                    if not v.isEnabled():
                        continue
                    item={'key': v.key, 'value': v.value, 'toreachvalue': None,
                          'valuestr': v.valuestr(),
                          'unit': v.unit, 'unitstr': v.unitstr(),
                          'flags': v.flags, 'age': int(v.age()), 'tag': v.tag}
                    if v.isWritable():
                        item['toreachvalue']=v.toReachValue
                    item['class']=v.__class__.__name__
                    item['error']=v.isError()
                    item['writable']=v.isWritable()
                    item['digital']=v.isDigital()
                    item['enable']=v.isEnabled()
                    item['manual']=v.isManual()
                    item['description']=v.description
                    items.append(item)

        data={'data': items}
        self.cb_write_json(handler, data)
        return True

    def cb_getvalues(self, handler, params):
        mbio=self.getMBIO()
        key=params.get('key')
        values=[]
        if key:
            v=mbio.value(key)
            if v is not None:
                values.append(v)
        else:
            values=mbio.values(params.get('filter'))

        items=[]
        for v in values:
            self.microsleep()
            if not v.isEnabled():
                continue
            item={'key': v.key, 'value': v.value, 'toreachvalue': None,
                    'valuestr': v.valuestr(),
                    'unit': v.unit, 'unitstr': v.unitstr(),
                    'flags': v.flags, 'age': int(v.age()), 'tag': v.tag}
            if v.isWritable():
                item['toreachvalue']=v.toReachValue
            item['class']=v.__class__.__name__
            item['error']=v.isError()
            item['writable']=v.isWritable()
            item['digital']=v.isDigital()
            item['enable']=v.isEnabled()
            item['manual']=v.isManual()
            item['description']=v.description
            items.append(item)

        data={'data': items}
        self.cb_write_json(handler, data)
        return True

    def cb_tasks(self, handler, params):
        handler.send_response(200)
        handler.send_header("Content-Type", "text/html; charset=utf-8")
        handler.end_headers()

        mbio=self.getMBIO()
        h=Html('Digimat MBIO Processor Monitor')

        data="""
            <div class="page container-fluid">
                <div class="card p-4 p-lg-5">
                    <div class="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-3">
                    <div>
                        <h1 class="h3 mb-1">Digimat MBIO Processor Monitor</h1>
                        <p class="text-secondary mb-0"><b>Tasks</b></p>
                    </div>
                    <div class="text-muted small">{mbio.version} / <a href="/gateways">Gateways</a> / <a href="/values">Values</a></div>
                    </div>
                    <table id="items" class="display nowrap" style="width:100%">
                    <thead>
                        <tr>
                            <th>Key</th>
                            <th>State</th>
                            <th>Age</th>
                            <th>Error</th>
                            <th>#Values</th>
                            <th>Class</th>
                        </tr>
                    </thead>
                    </table>
                </div>
            </div>
        """
        data=data.replace('{mbio.version}', mbio.version)
        h.write(data)

        data="""
        <script>
            $(function () {
                const table = new DataTable('#items', {
                responsive: true,
                paging: false,
                searching: true,
                ordering: true,
                info: false,
                search: {
                    smart: true,
                    regex: false,
                    caseInsensitive: true,
                    boundary: false
                },
                ajax: {
                    url: "/api/v1/gettasks",
                    dataSrc: "data"
                },
                columns: [
                    { data: "key" },
                    { data: "state",
                        render: function (data, type, row) {
                            if (type !== "display") return data;
                            return `<div class="d-flex justify-content-between align-items-center">
                                <span>${data}</span>
                                <button class="btn btn-sm btn-outline-secondary cell-action" data-id="${row.key}">
                                    Reset
                                </button>
                                </div>`;
                            }
                    },
                    { data: "statetime" },
                    { data: "error", render: v=>v ? 'ERROR' : '' },
                    { data: "countvalues" },
                    { data: "class" }
                ],
                rowCallback: function (row, data) {
                    if (data.error) {
                        $('td', row).css('background-color', 'pink');
                    }
                }
                });

                $("#items tbody").on("click", ".cell-action, .action-btn", async function (e) {
                    e.stopPropagation();
                    const row = table.row(this.closest('tr'));
                    const data = row.data();
                    try {
                        const r = await fetch(`/api/v1/resettask?key=${data.key}`, {method: "GET"});
                    } catch (err) {
                    }
                });

                $('#items').on('click','tr', function() {
                    var data = table.row(this).data();
                    const url = "/taskvalues?task=" + encodeURIComponent(data.key);
                    window.location.href = url;
                });

                setInterval(function () {
                    table.ajax.reload(null, false);
                    }, 1000);

            });
        </script>
        """
        h.write(data)
        handler.wfile.write(h.bytes())

    def cb_gateways(self, handler, params):
        handler.send_response(200)
        handler.send_header("Content-Type", "text/html; charset=utf-8")
        handler.end_headers()

        mbio=self.getMBIO()
        h=Html('Digimat MBIO Processor Monitor')

        data="""
            <div class="page container-fluid">
                <div class="card p-4 p-lg-5">
                    <div class="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-3">
                    <div>
                        <h1 class="h3 mb-1">Digimat MBIO Processor Monitor</h1>
                        <p class="text-secondary mb-0"><b>Gateways</b></p>
                    </div>
                    <div class="text-muted small">{mbio.version} / <a href="/tasks">Tasks</a> / <a href="/values">Values</a></div>
                    </div>
                    <table id="items" class="display nowrap" style="width:100%">
                    <thead>
                        <tr>
                            <th>Key</th>
                            <th>Host</th>
                            <th>MAC</th>
                            <th>State</th>
                            <th>Error</th>
                            <th>#Devices</th>
                            <th>Class</th>
                        </tr>
                    </thead>
                    </table>
                </div>
            </div>
        """
        data=data.replace('{mbio.version}', mbio.version)
        h.write(data)

        data="""
        <script>
            $(function () {
                const table = new DataTable('#items', {
                responsive: true,
                paging: false,
                searching: true,
                ordering: true,
                info: false,
                search: {
                    smart: true,
                    regex: false,
                    caseInsensitive: true,
                    boundary: false
                },
                ajax: {
                    url: "/api/v1/getgateways",
                    dataSrc: "data"
                },
                columns: [
                    { data: "key" },
                    { data: "host" },
                    { data: "mac" },
                    { data: "state",
                        render: function (data, type, row) {
                            if (type !== "display") return data;
                            return `<div class="d-flex justify-content-between align-items-center">
                                <span>${data}</span>
                                <button class="btn btn-sm btn-outline-secondary cell-action" data-id="${row.key}">
                                    Reset
                                </button>
                                </div>`;
                            }
                    },
                    { data: "error", render: v=>v ? 'ERROR' : '' },
                    { data: "countdevices" },
                    { data: "class" }
                ],
                rowCallback: function (row, data) {
                    if (data.error) {
                        $('td', row).css('background-color', 'pink');
                    }
                }
                });

                $("#items tbody").on("click", ".cell-action, .action-btn", async function (e) {
                    e.stopPropagation();
                    const row = table.row(this.closest('tr'));
                    const data = row.data();
                    try {
                        const r = await fetch(`/api/v1/resetgateway?key=${data.key}`, {method: "GET"});
                    } catch (err) {
                    }
                });

                $('#items').on('click','tr', function() {
                    var data = table.row(this).data();
                    const url = "/devices?gateway=" + encodeURIComponent(data.key);
                    window.location.href = url;
                });

                $(document).on('keydown', function (e) {
                    if ($(e.target).is('input, textarea')) return;

                    if (!e.ctrlKey && !e.metaKey && !e.altKey && e.key === '/') {
                        e.preventDefault();
                        const searchInput = $('#dt-search-0.dt-input');
                        console.log(searchInput);
                        searchInput.focus();
                        searchInput.select();
                    }
                });

                setInterval(function () {
                    table.ajax.reload(null, false);
                    }, 1000);

            });
        </script>
        """
        h.write(data)
        handler.wfile.write(h.bytes())

    def cb_devices(self, handler, params):
        handler.send_response(200)
        handler.send_header("Content-Type", "text/html; charset=utf-8")
        handler.end_headers()

        mbio=self.getMBIO()
        h=Html('Digimat MBIO Processor Monitor')
        gateway=params.get('gateway')

        data="""
            <div class="page container-fluid">
            <div class="card p-4 p-lg-5">
            <div class="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-3">
            <div>
            <h1 class="h3 mb-1">Digimat MBIO Processor Monitor</h1>
            <p class="text-secondary mb-0"><a href="/gateways">Gateways</a> / <b>{gateway}</b> / devices</p>
            </div>
            <div class="text-muted small">{mbio.version} / <a href="/tasks">Tasks</a> / <a href="/values">Values</a></div>
            </div>
            <table id="items" class="display nowrap" style="width:100%">
            <thead>
            <tr>
            <th>Address</th>
            <th>Key</th>
            <th>Vendor</th>
            <th>Model</th>
            <th>Version</th>
            <th>State</th>
            <th>Age</th>
            <th>Error</th>
            <th>#Values</th>
            <th>#Msg</th>
            <th>#MsgErr</th>
            <th>IsManualValue</th>
            <th>Class</th>
            </tr>
            </thead>
            </table>
            </div>
            </div>
        """
        data=data.replace('{gateway}', gateway)
        data=data.replace('{mbio.version}', mbio.version)
        h.write(data)

        data="""
        <script>
            $(function () {
            const table = new DataTable('#items', {
            responsive: true,
            paging: false,
            searching: true,
            ordering: true,
            info: false,
            search: {
                smart: true,
                regex: false,
                caseInsensitive: true,
                boundary: false
            },
            ajax: {
                url: "/api/v1/getgatewaydevices?gateway={gateway}",
                dataSrc: "data"
            },
            columns: [
                { data: "address" },
                { data: "key" },
                { data: "vendor" },
                { data: "model" },
                { data: "version" },
                { data: "state",
                    render: function (data, type, row) {
                        if (type !== "display") return data;
                        return `<div class="d-flex justify-content-between align-items-center">
                            <span>${data}</span>
                            <button class="btn btn-sm btn-outline-secondary cell-action" data-id="${row.key}">
                                Reset
                            </button>
                            </div>`;
                        }
                },
                { data: "statetime" },
                { data: "error", render: v=>v ? 'ERROR' : '' },
                { data: "countvalues" },
                { data: "countmsg" },
                { data: "countmsgerr" },
                { data: "ismanualvalue", render: v=>v ? 'MAN' : '' },
                { data: "class" }
            ],
            rowCallback: function (row, data) {
                if (data.error) {
                    $('td', row).css('background-color', 'pink');
                }
            }
            });

            setInterval(function () {
                table.ajax.reload(null, false);
                }, 2000);

            $("#items tbody").on("click", ".cell-action, .action-btn", async function (e) {
                e.stopPropagation();
                const row = table.row(this.closest('tr'));
                const data = row.data();
                try {
                    const r = await fetch(`/api/v1/resetdevice?gateway=${data.gateway}&key=${data.key}`, {method: "GET"});
                } catch (err) {
                }
            });

            $('#items').on('click','tr', function() {
                var data = table.row(this).data();
                const url = "/devicevalues?gateway=" + encodeURIComponent('{gateway}')
                    + "&device=" + encodeURIComponent(data.key);
                window.location.href = url;
            });

            });
        </script>
        """

        data=data.replace('{gateway}', gateway)
        h.write(data)
        handler.wfile.write(h.bytes())

    def cb_taskvalues(self, handler, params):
        handler.send_response(200)
        handler.send_header("Content-Type", "text/html; charset=utf-8")
        handler.end_headers()

        mbio=self.getMBIO()
        h=Html('Digimat MBIO Processor Monitor')
        task=params.get('task')

        data="""
            <div class="page container-fluid">
                <div class="card p-4 p-lg-5">
                    <div class="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-3">
                    <div>
                        <h1 class="h3 mb-1">Digimat MBIO Processor Monitor</h1>
                        <p class="text-secondary mb-0"><a href="/tasks">Tasks</a> / <b>{task}</b> / values</p>
                    </div>
                    <div class="text-muted small">{mbio.version} / <a href="/gateways">Gateways</a> / <a href="/values">Values</a></div>
                    </div>
                    <table id="items" class="display nowrap" style="width:100%">
                    <thead>
                        <tr>
                            <th>Key</th>
                            <th>Manual</th>
                            <th>Value</th>
                            <th>SP</th>
                            <th>Flags</th>
                            <th>Age</th>
                            <th>Error</th>
                            <th>Tag</th>
                            <th>Label</th>
                        </tr>
                    </thead>
                    </table>
                </div>
            </div>
        """
        data=data.replace('{mbio.version}', mbio.version)
        data=data.replace('{task}', task)
        h.write(data)

        url=f"/api/v1/gettaskvalues?task={task}"
        data=self.getDataTableScriptForValues(url, 2000)
        h.write(data)

        handler.wfile.write(h.bytes())

    def cb_devicevalues(self, handler, params):
        handler.send_response(200)
        handler.send_header("Content-Type", "text/html; charset=utf-8")
        handler.end_headers()

        mbio=self.getMBIO()
        h=Html('Digimat MBIO Processor Monitor')
        gateway=params.get('gateway')
        device=params.get('device')

        url=f'/devices?gateway={gateway}'

        data="""
            <div class="page container-fluid">
                <div class="card p-4 p-lg-5">
                    <div class="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-3">
                    <div>
                        <h1 class="h3 mb-1">Digimat MBIO Processor Monitor</h1>
                        <p class="text-secondary mb-0"><a href="/gateways">Gateways</a> / <a href="{url}">{gateway}</a> / <b>{device}</b> / values</p>
                    </div>
                    <div class="text-muted small">{mbio.version} / <a href="/tasks">Tasks</a> / <a href="/values">Values</a></div>
                    </div>
                    <table id="items" class="display nowrap" style="width:100%">
                    <thead>
                        <tr>
                            <th>Key</th>
                            <th>Manual</th>
                            <th>Value</th>
                            <th>SP</th>
                            <th>Flags</th>
                            <th>Age</th>
                            <th>Error</th>
                            <th>Tag</th>
                            <th>Label</th>
                        </tr>
                    </thead>
                    </table>
                </div>
            </div>
        """
        data=data.replace('{mbio.version}', mbio.version)
        data=data.replace('{gateway}', gateway)
        data=data.replace('{device}', device)
        data=data.replace('{url}', url)
        h.write(data)

        url=f"/api/v1/getdevicevalues?gateway={gateway}&device={device}"
        data=self.getDataTableScriptForValues(url, 2000)
        h.write(data)

        handler.wfile.write(h.bytes())

    def getDataTableScriptForValues(self, url, timeoutReload=2000):
        data="""
        <script>
            $(function () {
                    const table = new DataTable('#items', {
                    rowId: 'key',
                    responsive: true,
                    paging: false,
                    searching: true,
                    ordering: true,
                    info: false,
                    search: {
                        smart: true,
                        regex: false,
                        caseInsensitive: true,
                        boundary: false
                    },
                    ajax: {
                        url: "{url}",
                        dataSrc: "data"
                    },

                    columns: [
                        { data: "key" },
                        { data: "manual", className: "editable",
                            render: function(value, type, row) {
                                if (type === "display") {
                                    if (row.writable && !row.error)
                                    {
                                        const checked = row.manual ? 'checked' : '';
                                        return `<label class="form-switch">
                                            <input type="checkbox" class="toggle-enabled"
                                            data-id="${row.key}" data-field="manual"
                                            ${checked}>
                                            <span class="slider"></span>
                                            </label>`;
                                    }

                                    return row.manual ? "MAN" : "AUTO";
                                 }

                                return value;
                            }
                        },
                        { data: "valuestr", className: "text-end" },
                        { data: "toreachvalue", className: "p0 editable text-start",
                          render: function(value, type, row)
                          {
                                if (type === "display")
                                {
                                    if (row.manual && row.writable)
                                    {
                                        if (row.digital)
                                        {
                                            const checked = row.toreachvalue ? 'checked' : '';
                                            return `<label class="form-switch">
                                                <input type="checkbox" class="toggle-enabled"
                                                data-id="${row.key}" data-field="toreachvalue"
                                                ${checked}>
                                                <span class="slider"></span>
                                                </label>`;
                                        }
                                        else
                                        {
                                            return `<input type="number" class="form-control form-control-sm edit-input"
                                                    data-id="${row.key}" data-field="toreachvalue"
                                                    value="${value ?? ''}">`;
                                        }
                                    }
                                 }

                                return value;
                            }
                        },
                        { data: "flags" },
                        { data: "age", render: v=>v<3600 ? v : '' },
                        { data: "error", render: v=>v ? 'ERROR' : '' },
                        { data: "tag" },
                        { data: "description" }
                    ],

                    rowCallback: function (row, data) {
                        if (!data.enable) {
                            $('td', row).css('background-color', 'lightgray');
                        } else if (data.error) {
                            $('td', row).css('background-color', 'pink');
                        } else if (data.manual) {
                            $('td', row).css('background-color', 'lightgreen');
                        } else {
                            $('td', row).css('background-color', 'white');
                        }
                    }
                });

                async function reloadRow(table, row) {
                    try {
                        data=row.data();
                        var r = await fetch(`/api/v1/getvalues?key=${data.key}`, {method: "GET"}).then(r=>r.json());
                        var newdata=r.data[0];
                        row.data(newdata);
                        row.invalidate();
                        table.draw(false);
                    } catch (_) {
                    }
                }

                let isUserEditing = false;
                let pollingId = setInterval(function() {
                  table.ajax.reload(null, false);
                  }, {timeout});

                $("#items tbody").on("change", ".toggle-enabled", async function (e) {
                    clearInterval(pollingId);
                    e.stopPropagation();

                    const $ui = $(this);
                    if ($ui.data('committing')) return;       // garde-fou
                    $ui.data('committing', true);

                    const $tr    = $ui.closest('tr');
                    const colKey = $ui.data('field');
                    const enabled = $ui.is(':checked');
                    const rowApi = table.row($tr);
                    const row    = rowApi.data();

                    try {
                        var res;
                        if (colKey=="toreachvalue") {
                            if (enabled) {
                                res = await fetch(`/api/v1/setvalue?key=${row.key}&value=1`, {method: "GET"});
                            } else {
                                res = await fetch(`/api/v1/setvalue?key=${row.key}&value=0`, {method: "GET"});
                            }
                        }
                        else {
                            if (enabled) {
                                v=row.toreachvalue;
                                if (v === null)
                                    v=row.value;
                                res = await fetch(`/api/v1/setvalue?key=${row.key}&value=${v}`, {method: "GET"});
                            } else {
                                res = await fetch(`/api/v1/setvalueauto?key=${row.key}`, {method: "GET"});
                            }
                        }

                        reloadRow(table, rowApi);

                        pollingId = setInterval(function() {
                            table.ajax.reload(null, false);
                            }, 10000);

                        if (!res.ok) throw new Error();
                    } catch (_) {
                        //$(this).prop("checked", !enabled);
                    } finally {
                        $ui.data('committing', false);
                    }
                });

                // ENTER => on empêche la soumission et on force le blur (ce qui déclenchera 'change')
                $('#items tbody').on('keydown', 'input.edit-input', function (e) {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        this.blur(); // provoque un 'change' si la valeur a été modifiée
                    }
                });

                // CHANGE (et donc aussi BLUR si la valeur a changé) => commit
                $('#items tbody').on('change', 'input.edit-input', async function () {
                const $ui = $(this);
                if ($ui.data('committing')) return;       // garde-fou
                $ui.data('committing', true);

                const colKey = $ui.data('field');
                const $tr    = $ui.closest('tr');
                const rowApi = table.row($tr);
                const row    = rowApi.data();

                    const original = row[colKey];
                    let newVal = $ui.val().trim();

                    if (String(original) === String(newVal)) {
                        $ui.data('committing', false);
                        return;
                    }

                    try {
                        const res = await fetch(`/api/v1/setvalue?key=${row.key}&value=${newVal}`, {method: 'GET'});
                        row[colKey] = newVal;
                        rowApi.data(row).draw(false);
                    } catch (err) {
                    } finally {
                        $ui.data('committing', false);
                    }
                });

                $(document).on('keydown', function (e) {
                    const $target=$(e.target);
                    const $searchInput = $('#dt-search-0.dt-input');


                    /*
                    if ($target!=$searchInput && $target.is('input, textarea'))
                        return;
                    */

                    if (!e.ctrlKey && !e.metaKey && !e.altKey && e.key === '/') {
                        e.preventDefault();
                        $searchInput.focus();
                        $searchInput.select();
                    } else if (e.ctrlKey && !e.metaKey && !e.altKey && e.key.toLowerCase() === 'r') {
                        e.preventDefault();
                        rows=table.rows({ search: 'applied' });
                        if (rows.count()>0 && rows.count()<=64)
                        {
                            rows.every(function () {
                                reloadRow(table, this);
                            });
                        }
                    }
                });
            });
        </script>
        """

        data=data.replace('{url}', url)
        data=data.replace('{timeout}', str(timeoutReload))

        return data

    def cb_values(self, handler, params):
        handler.send_response(200)
        handler.send_header("Content-Type", "text/html; charset=utf-8")
        handler.end_headers()

        mbio=self.getMBIO()
        h=Html('Digimat MBIO Processor Monitor')

        data="""
            <div class="page container-fluid">
                <div class="card p-4 p-lg-5">
                    <div class="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-3">
                    <div>
                        <h1 class="h3 mb-1">Digimat MBIO Processor Monitor</h1>
                        <p class="text-secondary mb-0">MBIO / <b>Values</b></p>
                    </div>
                    <div class="text-muted small">{mbio.version} / <a href="/gateways">Gateways</a> / <a href="/tasks">Tasks</a></div>
                    </div>
                    <table id="items" class="display nowrap" style="width:100%">
                    <thead>
                        <tr>
                            <th>Key</th>
                            <th>Manual</th>
                            <th>Value</th>
                            <th>SP</th>
                            <th>Flags</th>
                            <th>Age</th>
                            <th>Error</th>
                            <th>Tag</th>
                            <th>Label</th>
                        </tr>
                    </thead>
                    </table>
                </div>
            </div>
        """
        data=data.replace('{mbio.version}', mbio.version)
        h.write(data)

        data=self.getDataTableScriptForValues('/api/v1/getvalues', 10000)
        h.write(data)

        handler.wfile.write(h.bytes())

    def onLoad(self, xml: XMLConfig):
        mbio=self.getMBIO()
        port=xml.getInt('port', 8001)
        # interface=mbio.interface
        interface='0.0.0.0'
        ws=TemporaryWebServer('/tmp/wsmonitor', port=port, host=interface, logger=self.logger)
        if ws:
            ws.registerGetCallback('/api/v1/gettasks', self.cb_gettasks)
            ws.registerGetCallback('/api/v1/getgateways', self.cb_getgateways)
            ws.registerGetCallback('/api/v1/getgatewaydevices', self.cb_getgatewaydevices)
            ws.registerGetCallback('/api/v1/gettaskvalues', self.cb_gettaskvalues)
            ws.registerGetCallback('/api/v1/getdevicevalues', self.cb_getdevicevalues)
            ws.registerGetCallback('/api/v1/getvalues', self.cb_getvalues)
            ws.registerGetCallback('/api/v1/setvalue', self.cb_setvalue)
            ws.registerGetCallback('/api/v1/setvalueauto', self.cb_setvalueauto)
            ws.registerGetCallback('/api/v1/resettask', self.cb_resettask)
            ws.registerGetCallback('/api/v1/resetgateway', self.cb_resetgateway)
            ws.registerGetCallback('/api/v1/resetdevice', self.cb_resetdevice)
            ws.registerGetCallback('/test', self.cb_mycallback)
            ws.registerGetCallback('/tasks', self.cb_tasks)
            ws.registerGetCallback('/gateways', self.cb_gateways)
            ws.registerGetCallback('/devices', self.cb_devices)
            ws.registerGetCallback('/taskvalues', self.cb_taskvalues)
            ws.registerGetCallback('/devicevalues', self.cb_devicevalues)
            ws.registerGetCallback('/values', self.cb_values)
            ws.registerGetCallback('/monitor', self.cb_gateways)
            self._wserver=ws

    def poweron(self):
        ws=self.wserver
        if ws:
            ws.disableAutoShutdown()
            ws.linkPath('~/Dropbox/python/www')
            ws.linkPath('/usr/lib/www')
            ws.start()
        return True

    def poweroff(self):
        ws=self.wserver
        if ws:
            ws.stop()
        return True

    def run(self):
        return 1.0


if __name__ == "__main__":
    pass
