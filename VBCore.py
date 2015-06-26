from HTMLParser import HTMLParser


class Table(object):
    def __init__(self):
        self.table = []  

    def clear(self):
        self.table = []

    def append_line(self):
        self.table.append([])

    def append_element(self):
        self.table[-1].append({'data':'','hrefs':[]})

    def element(self, ij=(-1,-1)):
        i = ij[0]
        j = ij[-1]
        return self.table[i][j]

    def insert_to_element(self, data, puredata=1):
        if data and puredata:
            self.element()['data'] += data
        if data and not puredata:
            self.element()['hrefs'].append(data)

    def del_trush_lines(self,trush_lines):
        trush_lines.sort(reverse=True)
        for l in trush_lines:
            del self.table[l]

    def del_trush_cols(self,trush_cols):
        trush_cols.sort(reverse=True)
        for line in self.table:
            for c in trush_cols:
                del line[c]

    def manage_table(self):
        pass

    def print_elementwise_matches(self, what):
        for i in self.table:
            for k in range(len(i)):
                if i[k] != []:
                    toprint = i[k][what]
                else:
                    toprint = ' '
                if k in (5,7):
                    print "%30s" % toprint,
                else:
                    if k == len(i)-1:
                        print "%30s" % i[k]['hrefs']
                    else:
                        print "%11s" % toprint,
            
    def print_elementwise_odds(self, what):
        for i in self.table:
            for k in range(len(i)):
                if i[k] != []:
                    toprint = i[k][what]
                else:
                    toprint = ' '
                if k == len(i)-1:
                    print "%19s" % toprint
                if k == 0:
                    print "%19s" % toprint,
                if k not in (0,len(i)-1):
                    print "%9s" % toprint,

    def print_elementwise_simple(self, what):
        for i in self.table:
            for k in range(len(i)):
                if i[k] != []:
                    toprint = i[k][what]
                else:
                    toprint = ' '
                if k == len(i)-1:
                    print "%30s" % i[k][what]
                else:
                    print "%25s" % toprint,


class TableExtractor(HTMLParser, Table):
    def __init__(self, which_table):
        HTMLParser.__init__(self)
        Table.__init__(self)

        self.table_start = False
        self.tr_start = False
        self.in_table = False
        self.table_count = 0
        self.looking_for_table = which_table
        self.table_found = False

    def feed(self,data):
        HTMLParser.feed(self, data)
        self.table_count = 0

    def handle_starttag(self, tag, attrs):
        self.handle_tags(tag, attrs, 1)

    def handle_endtag(self, tag):
        self.handle_tags(tag, None, 0)

    def handle_data(self, data):
        if self.in_table:
            self.insert_to_element(self.data_cleanup(data))

    def handle_tags(self, tag, attrs, start):
        if attrs == None:
            attrs = {}
        else:
            attrs = dict(attrs)

        if tag == 'table':
            if start:
                self.table_count += 1
                self.table_found = self.table_count == self.looking_for_table
                self.table_start = self.table_found
            if not start:
                self.table_start = False

        if tag == 'tr' and self.table_found:
            if start:
                self.append_line()
                self.tr_start = True
            else:
                self.tr_start = False

        if tag == 'td' and self.table_found:
            if start:
                self.append_element()
                self.in_table = self.table_start and self.tr_start
            else:
                self.in_table = False

        if tag =='a':
            if start:
                if self.in_table:
                    attrs['href'] = self.data_cleanup(attrs['href'])
                    if 'href' in attrs and \
                            (attrs['href'] is not None and \
                            not attrs['href'].startswith('#') and \
                            not attrs['href'].startswith('javascript')):
                        self.insert_to_element(attrs['href'],0)

    def data_cleanup(self, data):
        data = data.replace('\t','')
        data = data.replace('\n','')
        data = data.replace('\r','')
        return data


class OxybetMatchList(TableExtractor):
    def __init__(self):
        which_table = 4
        TableExtractor.__init__(self,which_table)

    def feed(self, data):
        TableExtractor.feed(self, data)

    def manage_table(self):
        self.del_trush_lines(self.find_trush_lines())
        self.del_trush_cols([2,3,4,8,9,10,11,12,13,14,15,16,17])
        self.fill_starttime()
        self.fill_tournament()
        self.title_teams()
        self.join_match_link()
        self.dict_the_table()

    def find_trush_lines(self):
        tr = []
        for line_num in range(len(self.table)):
            if len(self.table[line_num]) == 0:
                tr.append(line_num)
        return tr

    def dict_the_table(self):
        dict_keys = ('starttime','tournament','inteam','score','outteam','link')
        for match in range(len(self.table)):
            dict_values = []
            for item in self.table[match]:
                dict_values.append(item['data']) 
            self.table[match] = dict(zip(dict_keys, dict_values))

    def fill_starttime(self):
        for match in self.table:
            if not match[0]['data'].endswith('-||-'):
                starttime = match[0]['data']
            else:
                match[0]['data'] = starttime

    def fill_tournament(self):
        for match in self.table:
            if not match[1]['data'].endswith('-||-'):
                assoc = match[1]['hrefs'][0].split('/')[1].replace('-',' ').title()
            match[1]['data'] = assoc

    def title_teams(self):
        for match in self.table:
            for team in (2,4):
                teamname = match[team]['data'].title().split(u' ')
                for wordcount in range(len(teamname)):
                    if teamname[wordcount].endswith(u'\u03c3'):
                        teamname[wordcount] = teamname[wordcount].rpartition(u'\u03c3')[0] + u'\u03c2'
                match[team]['data'] = u' '.join(teamname)
            
    def join_match_link(self):
        for match in self.table:
            match[-1]['data'] = 'http://www.oxybet.com' + match[-1]['hrefs'][0]

    def print_dict(self, item):
        for match in self.table:
            for toprint in item:
                print '%25s' % match[toprint],
            print '\n'


class OxybetOddsTable(TableExtractor):
    def __init__(self):
        which_table = 1
        TableExtractor.__init__(self,which_table)

    def feed(self,data):
        TableExtractor.feed(self,data)
        self.manage_table()
        self.dict_the_table()

    def manage_table(self):
        self.del_trush_lines([0])
        self.del_trush_cols([1,3,5,7,8])
        self.fix_bookername()
        self.float_odds()

    def dict_the_table(self):
        dict_keys = ('1','X','2','update')
        for booker in range(len(self.table)):
            dict_values = []
            for item in self.table[booker][1:]:
                dict_values.append(item['data']) 
            self.table[booker][1] = dict(zip(dict_keys, dict_values))
    
        self.table = {line[0]['data']:line[1] for line in self.table}

    def fix_bookername(self):
        for booker in range(len(self.table)):
            bookername = self.table[booker][0]['data']
            self.table[booker][0]['data'] = bookername.partition(' (')[0]

    def float_odds(self):
        trush_bookers = []
        for booker in range(len(self.table)):
            for point in (1,2,3):
                s = self.table[booker][point]['data']
                s = s.split(u',')
                if len(s) == 2 and s[0].isdigit() and s[1].isdigit():
                    self.table[booker][point]['data'] = float(u'.'.join(s))
                else:
                    trush_bookers.append(booker)
                    break
        self.del_trush_lines(trush_bookers)


    def print_dict(self, item):
        print "%15s%25s%25s%25s%25s" % ('Booker','1','X','2','Update')
        print "%115s" % (115*'-'),
        for booker in self.table:
            print '\n%15s' % booker,
            for toprint in item:
                print '%24s' % self.table[booker][toprint],


class Match(object):
    def __init__(self, attrs, odds):
        self.attrs = attrs
        self.odds = odds
        self.calc_ganiota()
        self.booker_odds = odds['Stoiximan']
        self.del_bookers(self.trush_bookers_list(('BetFair','Fdjeux','Iddaa','PublicBet','BetDaq'), 1.1))
        self.calc()
        #TODO: how many bookers left in self.odds

    def calc(self):
        self.calc_booker_probs()
        self.calc_mean_probs()
        self.calc_value()
        self.calc_billy()
        self.isvaluable = any( self.values[i] > 1. for i in self.values ) and len(self.odds) >= 10

    def calc_ganiota(self):
        for bkr in self.odds:
            ganiota = 0.0
            for odd in ('1', 'X', '2'):
                ganiota += 1./self.odds[bkr][odd]
            self.odds[bkr]['ganiota'] = ganiota

    def del_bookers(self, trush_bookers):
        for tb in trush_bookers:
            if self.odds.has_key(tb):
                self.odds.pop(tb)

    def trush_bookers_list(self,names,max_ganiota):
        tbl = list(names)
        for bkr in self.odds:
            if self.odds[bkr]['ganiota'] > max_ganiota:
                tbl.append(bkr)
        return tbl

    def calc_booker_probs(self):
        self.probs = {}
        for bkr in self.odds:
            self.probs[bkr] = {}
            for odd in ('1', 'X', '2'):
                self.probs[bkr][odd] = 1./(self.odds[bkr][odd]*self.odds[bkr]['ganiota'])

    def calc_mean_probs(self):
        self.mprobs = {'1': 0.0, '2': 0.0 , 'X': 0.0}
        for bkr in self.probs:
            for prob in self.mprobs:
                self.mprobs[prob] += self.probs[bkr][prob] 
        for prob in self.mprobs:
            self.mprobs[prob] = self.mprobs[prob]/float(len(self.probs))

    def calc_value(self):
        pnts = ('1','X','2')
        odds = self.booker_odds
        mprobs = self.mprobs
        self.values = {k:odds[k]*mprobs[k] for k in pnts}

    def calc_billy(self):
        pnts = ('1','X','2')
        odds = self.booker_odds
        values = self.values
        self.bet_ratio = {k:(values[k]-1)/(odds[k]-1) for k in pnts}

    def print_all(self):
        toprint = ('1', 'X', '2','ganiota')
        for bkr in self.odds:
            print '\n%15s' % bkr,
            for item in toprint:
                print '%15s' % self.odds[bkr][item],
            '''for item in toprint:
                print '%15s' % self.probs[bkr][item],'''
        print '\n'
        toprint = ('1', 'X', '2')
        for mp in toprint:
            print mp, ' | ', 'mprob', ' : ',self.mprobs[mp] ,'    val', ' : ', self.values[mp]
        for attr in self.attrs.iteritems():
            print '%15s:%65s' % attr

    def print_attrs(self):
        print "%71s" % (71*'=')
        print self.attrs['tournament'].ljust(40), self.attrs['starttime'].rjust(30)
        print "%70s." % (35*'. ')
        print "%31s%20s%20s" % (self.attrs['inteam'], self.attrs['score'],self.attrs['outteam'])
        print "%31s%20s%20s" % ('1','X','2')
        print "%10s:%20.2f%20.2f%20.2f" % ('odds', self.booker_odds['1'],self.booker_odds['X'],self.booker_odds['2'])
        print "%10s:%20.3f%20.3f%20.3f" % ('prob', self.mprobs['1'],self.mprobs['X'],self.mprobs['2'])
        a= {k:self.values[k]>1. for k in self.values}
        print "%10s:" % 'value',
        #print "%10s:%20.2f%20.2f%20.2f" % ('value', self.values['1'],self.values['X'],self.values['2'])
        for point in ('1','X','2'):
            if a[point]:
                print "%19.2f" % self.values[point],
            else:
                print "%19s" % '-',

        print "\n%10s:" % 'bet_ratio',
        for point in ('1','X','2'):
            if a[point]:
                print "%19.2f" % self.bet_ratio[point],
            else:
                print "%19s" % '-',
        print '\n'


