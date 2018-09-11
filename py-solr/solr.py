import json
import requests


class Solr:
    """Wrapper around a Solr server."""

    @staticmethod
    def _json_type(json_obj):
        """Returns the JSON object type as a string.

        That is, returns supported type of the top level JSON object
        (document).

        :param json json_obj:   Object to inspect
        :return:                One of 'array', 'features', 'object'  or
                                'unknown'
        """

        if type(json_obj) == list:
            return 'array'

        if type(json_obj) == dict:
            if 'features' in json_obj:
                return 'features'
            elif 'properties' in json_obj:
                return 'object'

        return 'unknown'

    @staticmethod
    def stats_to_mbb(json_stats):
        """ Converts JSON response to BBox format
        """

        box = [
            [json_stats['stats_fields'][
                 ('geometry.coordinates_%d___pdouble' % d)]['min'] for d in
             [0, 1, 2]],
            [json_stats['stats_fields'][
                 ('geometry.coordinates_%d___pdouble' % d)]['max'] for d in
             [0, 1, 2]]
        ]

        return box

    @staticmethod
    def _append_if_not_found(params, key, val, verbose=False):
        if val is None:
            return

        if not ([True for c in params if c == key]):
            params.append((key, val))
        else:
            if verbose:
                print('Warning, not appending ("%s", "%s") as "%s" is already'
                      ' present' % (key, val, key))

    @staticmethod
    def label_to_q(label):
        return 'properties.id:%s' % label

    @staticmethod
    def labels_to_q(labels):
        return ' OR '.join(['properties.id:%s' % l for l in labels])

    @staticmethod
    def point_to_str(coordinate):
        assert (len(coordinate) > 0)
        assert (len(coordinate) < 5)
        if coordinate is None:
            print('Coordinate: %s' % coordinate)
        return ', '.join(['%f' % c for c in coordinate])

    @staticmethod
    def mbb_to_str(mbb):
        # FIXME: Should we take into account the referenceSpace?
        assert (len(mbb) == 2)
        assert (len(mbb[0]) == len(mbb[1]))

        mbb_str = '["%s" TO "%s"]' % (Solr.point_to_str(mbb[0]),
                                      Solr.point_to_str(mbb[1]))

        return mbb_str

    def __init__(self, url='', cloud_mode=False):
        assert (url != '')
        self.service_url = url
        self.cloud_mode = cloud_mode

    #########################################################################
    # GET APIs
    #########################################################################
    def _get(self, endpoint, params, print_timing=False, verbose=False):
        """Execute a REST API call."""

        r = requests.get('%s/%s' % (self.service_url, endpoint), params)

        if verbose or r.status_code != requests.codes.ok:
            print('get: %s : %s' % (r.url, r.status_code))
            print('params:')
            print(json.dumps(params, indent=2))
            print('result: %s' % r.reason)

        if print_timing and r.status_code == requests.codes.ok:
            rsp_json = r.json()
            queries = rsp_json['response']['numFound']
            timing = rsp_json['responseHeader']['QTime']
            print('QTime: %d [ms] # rows %d' %
                  (timing, queries))

        if r.status_code != requests.codes.ok:
            r.raise_for_status()

        return r

    def _get_core(self, core, endpoint, params,
                  print_timing=False, verbose=False):
        """API Calls to a specific core."""

        # if self.cloud_mode:
        #     existing_cores = getClusterCollections()
        # else:
        existing_cores = self.cores()

        if core not in existing_cores:
            print('ERROR: no collection with "%s" name exist!' % core)
            return

        return self._get('%s/%s' % (core, endpoint), params,
                         print_timing, verbose)

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

    def core_unload(self, core, verbose=False):
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
        (faster indexing, smaller index bucket_size, and faster range queries)
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

    #########################################################################
    # QUERY APIs
    #########################################################################

    @staticmethod
    def _point_to_fq(point):
        assert (len(point) > 1)
        assert (len(point) < 5)

        # FIXME: Take into account the reference space to compute
        # conversions if/when needed

        # FIXME: Evaluate what is better, the whole field, or to use the
        # scalar values of each geometry?

        # space_str + ' AND geometry.geometry=("%s")' %
        #           self.point_to_str(point)
        return ' AND '.join(['geometry.coordinates_%d___pdouble:%f' %
                             (d, point[d])
                             for d in [0, 1, 2, 3][:len(point)]])

    @staticmethod
    def mbb_to_fq(mbb):
        # FIXME: Take into account the reference space to compute
        # conversions if/when needed

        # FIXME: Evaluate what is better, a range query over the whole
        # field, or to use range queries over the scalar values of each
        # geometry?
        return 'geometry.coordinates:%s' % Solr.mbb_to_str(mbb)

    def _query(self, core, q='*:*', fq=None, fl=None, params=None,
               rows=10, start=0, wt='json', indent='on',
               print_timing=False, verbose=False):
        """Wrapper for combining both spatial and text-related search
        parameters.

        The result will be the intersection of all the filters and the query
        provided.

        An equivalent example of a direct REST API call:
           http://localhost:8983/solr/metadata/select?fq=geometry.coordinates:[-130,30%20TO%20-94,44]&q=abstract:*&wt=json

           :param str core:     targeted document collection
           :param str q:        query to execute. Defaults to '*:*'
           :param list[str] fq: filter query strings. Defaults to None.
           :param str fl:       comma separated list of document fields to be
                                returned the query (by default returns all).
           :param list[(str, str)] params:
                                GET parameters, allows to specify arbitrary
                                parameters not explicitly handled by this
                                method.
           :param int rows:     number of results to return. Defaults to 10.
           :param int start:    starting at (for paging). Defaults to 0.
           :param str wt:       response format. Defaults to 'json'
           :param str indent:   whether to indent or not the response.
                                Defaults to 'on'
           :param bool verbose: verbose mode (for debugging)
           :return:             the HTTP request result object
          """

        p = []
        if params is not None:
            p = params[:]
        self._append_if_not_found(p, 'q', q, verbose)
        self._append_if_not_found(p, 'rows', str(rows), verbose)
        self._append_if_not_found(p, 'start', str(start), verbose)
        self._append_if_not_found(p, 'wt', wt, verbose)
        self._append_if_not_found(p, 'indent', indent, verbose)
        self._append_if_not_found(p, 'fl', fl, verbose)

        # From:
        #  https://lucene.apache.org/solr/guide/6_6/common-query-parameters.html#CommonQueryParameters-Thefq_FilterQuery_Parameter
        #
        # The fq parameter defines a query that can be used to restrict the
        # superset of documents that can be returned, without influencing
        # score. It can be very useful for speeding up complex queries,
        # since the queries specified with fq are cached independently of the
        # main query. When a later query uses the same filter, there's a
        # cache hit, and filter results are returned quickly from the cache.
        if fq is not None:
            [p.append(('fq', f)) for f in fq]

        return self._get_core(core, 'select', p, print_timing, verbose)

    def spatial_mbb(self, core, query='*:*', params=None,
                    print_timing=False, verbose=False):
        """Computes spatial bounds (BBox) of a given query result.

        default query='*:*' matches all documents and thus returns bounds of
        the universe

        Args:
            core (str): the targeted collection.
            query (str): query string to execute.
            params (List): List of Solr query parameters.
            print_timing (bool): print query timing stats
            verbose (bool): verbose mode (for debugging)

        Returns:
            BBox: the bounding box of the query results.
        """
        p = []
        if params is not None:
            p = params[:]

        p.append(('stats', 'true'))
        [p.append(('stats.field', 'geometry.coordinates_%d___pdouble' % d))
         for d in [0, 1, 2]]
        p.append(('rows', 0))

        if verbose:
            print('spatial_bounds:')
        r = self._query(core, query, params=p, print_timing=print_timing,
                        verbose=verbose)

        return self.stats_to_mbb(r.json()['stats'])

    def query(self, core,
              oid=None, labels=None,
              geometry=None, mbb=None, reference_space=None,
              fl=None, q='*:*', params=None,
              rows=10, start=0,
              print_timing=False, verbose=False):
        """Wrapper for queries inside the spatial index.

            If a combination of oid, geometry, referenceSpace and/or mbb
            are provided, the query results will be an AND of all the provided
            parameters.

            *Note*: The labels are used to compute a minimum bounding box
            which will contain all the points of all the labels. This might
            contain space not in any of the labels which will successfully

            :param q:
            :param labels:
            :param core:
            :param oid:
            :param geometry: ("24.27, 9.84, 17.65")
            :param reference_space:
            :param mbb:         geometry.coordinates:["2, 9, 1" TO "250, 100,
                                180"]
            :param fl:
            :param params:
            :param rows:
            :param start:       row offset at which the output should start.

            :param print_timing: print query timing stats
            :param verbose:
            :return:
        """

        fq = []  # Query filters, list of predicates
        p = []  # make sure we do not modify caller's object

        # We are using a list of tuples instead of a dictionary as we can
        # have multiple time the same key.
        if params is not None:
            p = params[:]

        if oid is not None:
            # We want the geometry of the document oid (this can be a set
            # of points)
            fq.append('properties.id:%s' % oid)

        if reference_space is not None:
            # We want all the points stored in that reference coordinate system
            fq.append('geometry.referenceSpace_str:%s' % reference_space)

        if geometry is not None:
            # We want everything found at that specific point in space

            # FIXME: Take into account the reference space to compute
            # conversions if/when needed
            fq.append(self._point_to_fq(geometry))

        if mbb is not None:
            # We want everything within that minimum bounding box

            # FIXME: Take into account the reference space to compute
            # conversions if/when needed
            fq.append(self.mbb_to_fq(mbb))

        if labels is not None:
            # We want all the points within the space defined by the union of
            # the labels, but not in the space between the spaces.

            # To achieve this, we approximate the volume of each label to a
            # Minimum Bounding Box, and then we add a single filter which
            # consists of the union of these boxes, connected through OR
            # statements, instead of computing the Minimum Bounding Box of
            # all the labels at once. The latter would contain a lot of dead
            # space not belonging to any volume of the labels for which we
            # would return false positive.

            # FIXME: We currently only use the approximated volume of each
            #        label instead of the exact volumes.

            # FIXME: Can we combine into a single query the current query and
            #        the computation of the MBB of the labels? This currently
            #        generates a query per label, and then the query
            #        effectively asked for by the user.

            # Compute the mbb of each label
            labels_mbbs = [self.spatial_mbb(core, self.label_to_q(l),
                                            verbose=verbose) for l in labels]

            fq.append(' OR '.join([self.mbb_to_fq(m)
                                   for m in labels_mbbs]))

        if verbose:
            print('Solr query:')
        r = self._query(core, q, fq, fl, params=p, rows=rows,
                        start=start,
                        print_timing=print_timing, verbose=verbose)

        return r.json()

    def query_cardinality(self, core,
                          oid=None, labels=None,
                          geometry=None, mbb=None, reference_space=None,
                          fl=None, q='*:*', params=None,
                          print_timing=False, verbose=False):

        # Run the query, but force the number of returned results to zero as
        # we are only interested in the number of hits
        return self.query(core, oid, labels, geometry, mbb, reference_space, fl,
                          q, params, rows=0, start=0,
                          print_timing=print_timing,
                          verbose=verbose)["response"]["numFound"]
