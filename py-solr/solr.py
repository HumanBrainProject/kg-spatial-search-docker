import json
import requests


class Solr:
    """Wrapper around a Solr server."""

    @staticmethod
    def _json_type(json_obj):
        """Returns the JSON object type.

        That is, returns supported type of the top level JSON object
        (document).

        """

        if type(json_obj) == list:
            return 'array'

        if type(json_obj) == dict:
            if 'features' in json_obj:
                return 'features'
            elif 'properties' in json_obj:
                return 'object'

        return "unknown"

    def __init__(self, url='', cloud_mode=False):
        assert (url != '')
        self.service_url = url
        self.cloud_mode = cloud_mode

    #########################################################################
    # GET APIs
    #########################################################################
    def _get(self, endpoint, params, verbose=False):
        """Execute a REST API call."""

        r = requests.get('%s/%s' % (self.service_url, endpoint), params)

        if verbose or r.status_code != requests.codes.ok:
            print('get: %s : %s' % (r.url, r.status_code))
            print('params:')
            print(json.dumps(params, indent=2))
            print('result: %s' % r.reason)

        if r.status_code != requests.codes.ok:
            r.raise_for_status()

        return r

    def _get_core(self, core, endpoint, params, verbose=False):
        """API Calls to a specific core."""

        # if self.cloud_mode:
        #     existing_cores = getClusterCollections()
        # else:
        existing_cores = self.cores()

        if core not in existing_cores:
            print('ERROR: no collection with "%s" name exist!' % core)
            return

        return self._get('%s/%s' % (core, endpoint), params, verbose)

    def cores(self, verbose=False):
        """Returns list of currently running (existing) cores."""

        params = {
            'action': 'STATUS',
            'indexInfo': 'false',
            'wt': 'json'
        }

        r = self._get('admin/cores', params, verbose)
        keys = list(r.json()['status'].keys())

        if verbose:
            print('Solr cores: %s' % r.url)
            print('%s' % keys)

        return keys

    def core_status(self, core=None, verbose=False):
        """The STATUS action returns the status of all running Solr cores, or 
        status for only the named core.

        If core_name is not given (default), returns status of all cores. 
        Otherwise, returns status of a named core:

            http://localhost:8983/solr/admin/cores?action=STATUS&core=core0
        """

        params = {
            'action': 'STATUS',
            'indexInfo': 'false',
            'wt': 'json'
        }

        if core is not None:
            params['core'] = core

        if verbose:
            print('Solr core_status:')

        r = self._get('admin/cores', params, verbose)
        status = r.json()['status']

        return status

    # config_set='data_driven_schema_configs'
    def core_load(self, core, config_set='_default', verbose=False):
        """Creates a new core and registers it.

        If a Solr core with the given name already exists, it will continue to
        handle requests while the new core is initializing. When the new core
        is ready, it will take new requests and the old core will be unloaded.

            http://localhost:8983/solr/admin/cores?action=CREATE&name=coreX&instanceDir=path/to/dir&config=config_file_name.xml&dataDir=data

        Note that this command is the only one of the Core Admin API commands
        that does not support the core parameter. Instead, the name parameter
        is required, as shown below.

        It is equivalent to `./bin/solr create -c core_name`

        NOTE: the core.properties file is built as part of CREATE action. As
            such, the core.properties file must NOT exist before calling
            core_load( ).
        """

        existing_cores = self.cores(verbose)
        if core in existing_cores:
            print('Solr create: core with "%s" name already exist!' % core)
            return

        # cfg = 'configsets/_default/conf/solrconfig.xml'
        # other supported parameters with default values:
        #   instanceDir:    whatever is specified for "name" parameter is set
        #                   by default
        #   config:         name of the config file (i.e., solrconfig.xml)
        #                   relative to instanceDir.
        params = {
            'action': 'CREATE',
            'wt': 'json',
            'name': core,
            'config_set': config_set,
            'instanceDir': 'mycores/%s' % core
        }

        if verbose:
            print('Solr core_load:')

        self._get('admin/cores', params, verbose)

    def core_reload(self, core, verbose=False):
        """The RELOAD action loads a new core from the configuration of an 
        existing, registered Solr core.

        While the new core is initializing, the existing one will continue to
        handle requests. When the new Solr core is ready, it takes over and
        the old core is unloaded.

        This is useful when you've made changes to a Solr core's configuration
        on disk, such as adding new field definitions. Calling the RELOAD 
        action lets you apply the new configuration without having to restart
        the Web container.

            http://localhost:8983/solr/admin/cores?action=RELOAD&core=core0
        """
        params = {
            'action': 'RELOAD',
            'wt': 'json'
        }

        if core is not None:
            params['core'] = core
        else:
            print('Solr reload: missing mandatory argument "core"')
            return

        if verbose:
            print('Solr core_reload:')

        self._get('admin/cores', params, verbose)

    def core_unload(self, core, verbose=True):
        """Removes a given core from Solr.

        Active requests will continue to be processed, but no new requests will
        be sent to the named core. If a core is registered under more than
        one name, only the given name is removed.

            http://localhost:8983/solr/admin/cores?action=UNLOAD&core=core0

        The UNLOAD action requires a parameter (core) identifying the core to
        be removed. If the persistent attribute of <solr> is set to true,
        the <core> element with this name attribute will be removed from
        solr.xml.

        It is equivalent to `./bin/solr delete -c corename`
        """

        existing_cores = self.cores()
        if core not in existing_cores:
            print('Solr unload: no core with "%s" name' % core)
            return

        params = {
            'action': 'UNLOAD',
            'wt': 'json',
            'core': core,
            'deleteIndex': 'true',
            'deleteDataDir': 'true',
            'deleteInstanceDir': 'true'
        }

        # the params deleteIndex, deleteDataDir, deleteInstanceDir are by
        # default set to false
        #     req = ((service_url + 'admin/cores?action=%s&core=%s&deleteIndex=true&deleteDataDir=true&deleteInstanceDir=true')
        #                   % (ACTION, core))
        if verbose:
            print('Solr core_unload:')

        self._get('admin/cores', params, verbose)

    def schema_fields(self, core, fields=None, show_defaults=False,
                      verbose=False):
        """List schema fields of a given collection.

        If show_defaults == True, all default field properties from each field's
        field type will be included in the response (e.g., tokenized for
        solr.TextField). If show_defaults == false, only explicitly specified
        field properties will be included.
        """
        defaults = 'true' if show_defaults else 'false'
        params = {
            'wt': 'json',
            'showDefaults': defaults
        }

        if fields is not None:
            params['fl'] = fields

        if verbose:
            print('Solr schema_fields:')

        r = self._get_core(core, 'schema/field', params, verbose)

        return r

    def schema_field_type_names(self, core, tag='name', verbose=False):
        # tag='class'
        params = {
            'wt': 'json'
        }

        if verbose:
            print('Solr schema_field_type_names:')

        r = self._get_core(core, 'schema/fieldtypes', params, verbose)

        field_list = []
        for field in r.json()['fieldTypes']:
            field_list.append(field[tag])

        return field_list

    def schema_field_names(self, core, names_of='fields', verbose=False):
        # names_of must be of these:
        json_names = {'fields': 'fields', 'dynamicfields': 'dynamicFields',
                      'fieldtypes': 'fieldTypes', 'copyfields': 'copyFields'}

        params = {
            'wt': 'json'
        }

        if verbose:
            print('Solr schema_field_names:')

        r = self._get_core(core, 'schema/%s' % names_of, params,
                           verbose)

        field_list = []
        for field in r.json()[json_names[names_of]]:
            field_list.append(field['name'])

        return field_list

    #########################################################################
    # POST APIs
    #########################################################################
    def _post(self, endpoint, headers, payload, verbose=False):
        """Execute a REST API call."""

        r = requests.post('%s/%s' % (self.service_url, endpoint), json=payload,
                          headers=headers)

        if verbose or r.status_code != requests.codes.ok:
            print('post: %s : %s' % (r.url, r.status_code))
            print('headers:')
            print(json.dumps(headers, indent=2))
            print('data:')
            print(json.dumps(payload, indent=2))
            print('result: %s' % r.reason)

        if r.status_code != requests.codes.ok:
            r.raise_for_status()

        return r

    def _post_core(self, core, endpoint, headers, payload, verbose=False):
        """API Calls to a specific core."""

        # if self.cloud_mode:
        #     existing_cores = getClusterCollections()
        # else:
        existing_cores = self.cores()

        if core not in existing_cores:
            print('ERROR: no collection with "%s" name exist!' % core)
            return

        return self._post('%s/%s' % (core, endpoint), headers, payload,
                          verbose)

    def create_kd_double_point_type(self, core, type_name, num_dims,
                                    verbose=False):
        """Adds a new field type backed up by solr.DoublePointField

        This is the core (spatial) data type that uses the newest features of
        Lucene. It functions similarly to TrieDoubleField, but using a
        "Dimensional Points" based data structure (blocked KD-trees) under the
        hood instead of indexed terms, and doesn't require configuration of a
        precision step. For single valued fields, docValues="true" must be
        used to enable sorting.

        Up to 4 dimensions are supported. It performs better in many ways
        (faster indexing, smaller index size, and faster range queries)
        compared to the previous TrieDoubleField-based alternatives (that work
        only with geodetic spatial data).
        """

        if type_name in self.schema_field_type_names(core):
            if verbose:
                print('Solr create_kd_double_point_type: "%s" fieldType name '
                      'exist!' % type_name)
            return

        if num_dims > 4:
            print('solr_create_kd_double_point_type: data dimensionality '
                  'must be < 5!')
            return

        post_header = {
            'Content-type': 'application/json',
            'charset': 'utf-8'
        }

        binary_data = {
            'add-field-type': {
                'name': type_name,
                'class': 'solr.PointType',
                'subFieldType': 'pdouble',  # solr.DoublePointField
                'dimension': num_dims
            }
        }

        if verbose:
            print('Solr create_kd_double_point_type:')

        self._post_core(core, 'schema', post_header, binary_data, verbose)

    def field_add(self, core, field_name, field_type, stored=False,
                  indexed=False, multi=False, doc_values=False, verbose=False):
        """Adds a new field.

        Adds a new field definition to your schema. If a field with the same
        name exists an error is thrown.

        All attributes are described in detail in the section [Defining
        Fields](https://cwiki.apache.org/confluence/display/solr/Defining+Fields).

        E.g.:
            curl -X POST -H 'Content-type:application/json' --data-binary '{
                "add-field":{
                    "name":"sell-by",
                    "type":"tdate",
                    "stored":true }
            }' http://localhost:8983/solr/gettingstarted/schema
        """

        if field_name in self.schema_field_names(core):
            if verbose:
                print('Solr field_add: "%s" field name '
                      'exist!' % field_name)
            return

        post_header = {
            'content-type': 'application/json',
            'charset': 'utf-8'
        }

        properties = {
            'name': field_name,
            'type': field_type,
            'stored': str(stored).lower(),
            'indexed': str(indexed).lower(),
            'multiValued': str(multi).lower(),
            'docValues': str(doc_values).lower()
        }

        binary_data = {
            'add-field': properties
        }

        if verbose:
            print('Solr field_add:')

        self._post_core(core, 'schema', post_header, binary_data, verbose)

    def field_delete(self, core, field_name, verbose=False):
        """Deletes field in a given document.

        The delete-field command removes a field definition from your schema.
        If the field does not exist in the schema, or if the field is the
        source or destination of a copy field rule, an error is thrown.

        All attributes are described in detail in the section [Defining
        Fields](https://cwiki.apache.org/confluence/display/solr/Defining+Fields).

        E.g.: to delete a field named "sell-by", you would POST the following
        request:

            curl -X POST -H 'Content-type:application/json' --data-binary '{
                "delete-field" : { "name":"sell-by" }
            }' http://localhost:8983/solr/metadata/schema
        """

        if field_name not in self.schema_field_names(core, names_of='fields'):
            print('Solr field_delete: "%s" fieldname does not exist!' %
                  field_name)
            return

        post_header = {
            'Content-type': 'application/json',
            'charset': 'utf-8'
        }

        binary_data = {
            'delete-field': {'name': field_name}
        }

        if verbose:
            print('Solr field_delete:')

        self._post_core(core, 'schema', post_header, binary_data, verbose)

    def commit(self, core, verbose=False):
        """Performs JSON-based commit

        The *commit* operation writes all documents loaded since the last
        commit to one or more segment files on the disk. Before a commit has
        been issued, newly indexed content is not visible to searches. The
        commit operation opens a new searcher, and triggers any event
        listeners that have been configured.
        """

        post_header = {
            'Content-Type': 'application/json',
            'charset': 'utf-8'
        }

        binary_data = {
            'commit': {}
        }

        if verbose:
            print('Solr commit:')

        self._post_core(core, 'update', post_header, binary_data, verbose)

    def index_spatial_json_doc(self, doc, core, commit=True,
                               print_timing=False, verbose=False):
        """Index/load GeoJSON-like docs representing spatial metadata.

        The given doc must be a valid GeoJSON-like format supported by
        SpatialSearchApp.
        """

        # docs must be JSON loaded as follows:
        # docs = json.load( open('spatial-metadata/records_0-100.json') )

        # This is how we *flatten* all fields out and map them using the
        # same (most inner) json tag:
        doc_type = self._json_type(doc)
        params = '?split=/'
        num_docs = 0

        if doc_type == 'array' or doc_type == 'object':
            num_docs = len(doc)
        elif doc_type == 'features':
            num_docs = len(doc['features'])
        else:
            print('Warning: unsupported JSON document. Skipping... ')
            return

        # FIXME: Should we try to actively hide the automatic, typed (
        # _str, ___pdouble, etc) fields?

        post_header = {
            'content-type': 'application/json',
            'charset': 'utf-8'
        }

        if verbose:
            print('Solr index_spatial_json_doc:')

        r = self._post_core(core, 'update/json/docs' + params,
                            post_header, doc, verbose)

        if commit:
            self.commit(core)

        if print_timing:
            rsp_json = r.json()
            print('QTime: %d[ms] # Queries %d: %d q/s ' %
                  (rsp_json['responseHeader']['QTime'], num_docs,
                   num_docs * 1000 / rsp_json['responseHeader']['QTime']))

    def index_spatial_json(self, url, core, commit=True, print_timing=False,
                           verbose=False):
        """Index/load GeoJSON-like docs representing spatial metadata.

        The given doc must be a valid GeoJSON-like format supported by
        SpatialSearchApp.
        """

        assert (url != '')
        docs = json.load(open(url))

        self.index_spatial_json_doc(docs, core, commit, print_timing, verbose)

    def delete(self, core, query='*:*', verbose=False):
        """Delete elements from a core."""

        post_header = {
            'Content-type': 'text/json',
            'charset': 'utf-8'
        }

        binary_data = {
            'delete': {'query': query},
            'commit': {}
        }

        if verbose:
            print('Solr delete:')

        r = self._post_core(core, 'update', post_header, binary_data, verbose)

        if r.status_code == requests.codes.ok:
            self.commit(core, verbose)