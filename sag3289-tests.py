import os

from flask_testing import TestCase

import interswellar.views as views
from interswellar import create_app
from interswellar.models import db, Star, Exoplanet, Constellation, Publication


class APITest(TestCase):

    ''' Tests API routes '''

    def create_app(self):
        return create_app(os.environ.get('APP_ENV', 'dev') + '_test')

    def setUp(self):
        db.create_all()
        self.populateDB()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def populateDB(self):
        star1 = Star(
            id=1, name='rouge_star', mass=1.0, luminosity=1.0, temperature=1000,
            radius=1.0
        )
        star2 = Star(
            id=2, name='star',  mass=2.0, luminosity=2.0, temperature=2000,
            radius=2.0
        )
        planet1 = Exoplanet(
            id=1, name='earth',  mass=1.0, radius=1.0, orbital_period=365,
            year_discovered=0
        )
        planet2 = Exoplanet(
            id=2, name='planet', mass=1.0, radius=1.0, orbital_period=1000000,
            year_discovered=2000
        )
        planet3 = Exoplanet(
            id=3, name='jonathan', mass=88.8, radius=44.4, orbital_period=0,
            year_discovered=1994
        )
        constel1 = Constellation(
            id=1, name='little_dipper', abbrev='ld', family='dd',
            meaning='Little Dipper', area=100
        )
        constel2 = Constellation(
            id=2, name='big_dipper',    abbrev='bd', family='dd',
            meaning='Big Dipper',    area=300
        )
        publ1 = Publication(
            id=1, ref='2008A&A...474..293B', title='Local Star Discovered',
            authors='Neil deGrasse Tyson', journal='Astronomy & Astrophysics',
            abstract='Former toaster in sky is actually a star'
        )
        publ2 = Publication(
            id=2, ref='2009A&A...434..421A', title='Bountiful Discoveries made',
            authors='Monkey Monkey, Bill Nye', journal='Astronomy & Astrophycis',
            abstract='This publication lists discoveries of constellation, planets, and stars'
        )

        planet3.star = star1
        planet3.discovered_by = publ2
        publ1.exoplanets = [planet1, planet2]
        publ1.stars = [star1, star2]
        star2.exoplanets = [planet1, planet2]
        constel1.stars = [star1, star2]

        db.session.add(star1)
        db.session.add(star2)
        db.session.add(planet1)
        db.session.add(planet2)
        db.session.add(planet3)
        db.session.add(constel1)
        db.session.add(constel2)
        db.session.add(publ1)
        db.session.add(publ2)
        db.session.commit()

    def test_stars_all(self):
        resp = self.client.get('/api/v1/stars')
        self.assertEqual(resp.mimetype, 'application/json')
        data = resp.json
        self.assertEqual(data['num_results'], 2)
        star1 = data['objects'][0]
        star2 = data['objects'][1]
        self.assertEqual(star1['id'], 1)
        self.assertEqual(star2['id'], 2)
        self.assertEqual(star2['name'], 'star')
        self.assertEqual(star2['mass'], 2.0)
        self.assertEqual(star2['luminosity'], 2.0)
        self.assertEqual(star1['radius'], 1.0)
        self.assertEqual(star1['temperature'], 1000)

    def test_stars_single(self):
        resp = self.client.get('/api/v1/stars/1')
        self.assertEqual(resp.mimetype, 'application/json')
        data = resp.json
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['name'], 'rouge_star')
        self.assertEqual(data['mass'], 1.0)
        self.assertEqual(data['luminosity'], 1.0)
        self.assertEqual(data['temperature'], 1000)
        self.assertEqual(data['radius'], 1.0)

    def test_stars_relationship(self):
        resp = self.client.get('/api/v1/stars/2')
        self.assertEqual(resp.mimetype, 'application/json')
        data = resp.json
        self.assertEqual(data['exoplanets'][0]['id'], 1)
        self.assertEqual(data['exoplanets'][1]['id'], 2)
        self.assertEqual(data['constellation']['id'], 1)
        self.assertEqual(data['discovered_by']['id'], 1)

    def test_planet_all(self):
        resp = self.client.get('/api/v1/exoplanets')
        self.assertEqual(resp.mimetype, 'application/json')
        data = resp.json
        self.assertEqual(data['num_results'], 3)
        planet1 = data['objects'][0]
        planet2 = data['objects'][1]
        planet3 = data['objects'][2]
        self.assertEqual(planet1['id'], 1)
        self.assertEqual(planet2['id'], 2)
        self.assertEqual(planet3['id'], 3)
        self.assertEqual(planet1['name'], 'earth')
        self.assertEqual(planet1['mass'], 1.0)
        self.assertEqual(planet1['radius'], 1.0)
        self.assertEqual(planet1['orbital_period'], 365)
        self.assertEqual(planet1['year_discovered'], 0)

    def test_planet_single(self):
        resp = self.client.get('/api/v1/exoplanets/2')
        self.assertEqual(resp.mimetype, 'application/json')
        data = resp.json
        self.assertEqual(data['id'], 2)
        self.assertEqual(data['name'], 'planet')
        self.assertEqual(data['mass'], 1.0)
        self.assertEqual(data['radius'], 1.0)
        self.assertEqual(data['orbital_period'], 1000000)
        self.assertEqual(data['year_discovered'], 2000)

    def test_planet_relationship(self):
        resp = self.client.get('/api/v1/exoplanets/3')
        self.assertEqual(resp.mimetype, 'application/json')
        data = resp.json
        self.assertEqual(data['id'], 3)
        self.assertEqual(data['star']['id'], 1)
        self.assertEqual(data['discovered_by']['id'], 2)

    def test_constellation_all(self):
        resp = self.client.get('/api/v1/constellations')
        self.assertEqual(resp.mimetype, 'application/json')
        data = resp.json
        self.assertEqual(data['num_results'], 2)
        const1 = data['objects'][0]
        const2 = data['objects'][1]
        self.assertEqual(const1['id'], 1)
        self.assertEqual(const2['id'], 2)
        self.assertEqual(const1['name'], 'little_dipper')
        self.assertEqual(const2['meaning'], 'Big Dipper')
        self.assertEqual(const1['abbrev'], 'ld')
        self.assertEqual(const2['area'], 300)

    def test_constellation_single(self):
        resp = self.client.get('/api/v1/constellations/1')
        self.assertEqual(resp.mimetype, 'application/json')
        data = resp.json
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['name'], 'little_dipper')
        self.assertEqual(data['abbrev'], 'ld')
        self.assertEqual(data['family'], 'dd')
        self.assertEqual(data['meaning'], 'Little Dipper')
        self.assertEqual(data['area'], 100)

    def test_constellation_relationship(self):
        resp = self.client.get('/api/v1/constellations/1')
        self.assertEqual(resp.mimetype, 'application/json')
        data = resp.json
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['stars'][0]['id'], 1)
        self.assertEqual(data['stars'][1]['id'], 2)

    def test_publication_single(self):
        resp = self.client.get('/api/v1/publications/1')
        self.assertEqual(resp.mimetype, 'application/json')
        data = resp.json
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['ref'], '2008A&A...474..293B')
        self.assertEqual(data['title'], 'Local Star Discovered')
        self.assertEqual(data['authors'], 'Neil deGrasse Tyson')
        self.assertEqual(data['journal'], 'Astronomy & Astrophysics')
        self.assertEqual(
            data['abstract'], 'Former toaster in sky is actually a star')

    def test_publication_relationship(self):
        resp = self.client.get('/api/v1/publications/1')
        self.assertEqual(resp.mimetype, 'application/json')
        data = resp.json
        self.assertEqual(data['id'], 1)
        stars = data['stars']
        planets = data['exoplanets']
        self.assertEqual(len(stars), 2)
        self.assertEqual(len(planets), 2)
        for i in range(2):
            self.assertEqual(stars[i]['id'], i + 1)
            self.assertEqual(planets[i]['id'], i + 1)
        self.assertEqual(planets[0]['name'], 'earth')
import os

from flask_testing import TestCase

from interswellar import create_app
from interswellar.models import db, Star, Exoplanet, Constellation, Publication


class ModelsTest(TestCase):

    """ Tests the models """

    def create_app(self):
        return create_app(os.environ.get('APP_ENV', 'dev') + '_test')

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_stars1(self):
        star1 = Star(id=1, name='Sun', mass=1.0,
                     luminosity=1.0, temperature=5000, radius=1.0)
        star2 = Star(id=3, name='Lummes', mass=5.0,
                     luminosity=3.0, temperature=6000, radius=2.7)
        db.session.add(star1)
        db.session.add(star2)
        db.session.commit()
        stars = Star.query.all()
        self.assertTrue(star1 in stars)
        self.assertTrue(star2 in stars)
        self.assertEqual(len(stars), 2)

    def test_stars2(self):
        star = Star(id=2, name='Aries', mass=3.0,
                    luminosity=4.0, temperature=7000, radius=3.0)
        db.session.add(star)
        db.session.commit()
        stars = Star.query.all()
        self.assertTrue(star in stars)
        self.assertEqual(stars[0].id, 2)
        self.assertEqual(stars[0].radius, 3.0)

    def test_stars3(self):
        star = Star(id=2, name='Aries', mass=3.0,
                    luminosity=4.0, temperature=7000, radius=3.0)
        db.session.add(star)
        db.session.commit()
        stars = Star.query.all()
        self.assertTrue(star in stars)
        self.assertEqual(stars[0].name, 'Aries')

    def test_stars4(self):
        star1 = Star(id=2, name='Aries', mass=3.0,
                     luminosity=4.0, temperature=7000, radius=3.0)
        star2 = Star(id=3, name='Lummes', mass=5.0,
                     luminosity=3.0, temperature=6000, radius=2.7)
        constellation = Constellation(
            id=1, name='big dipper', abbrev='big dp',
            family='arris', meaning='laddle', area=56.54)
        constellation.stars = [star1, star2]
        db.session.add(star1)
        db.session.add(star2)
        db.session.add(constellation)
        db.session.commit()
        constellations = Constellation.query.all()
        self.assertIn(star1, constellations[0].stars)
        self.assertIn(star2, constellations[0].stars)

    def test_exoplant1(self):
        exoplanet1 = Exoplanet(
            id=1, name='Earth', mass=0.2, radius=1.0, orbital_period=5000, year_discovered=0)
        exoplanet2 = Exoplanet(
            id=2, name='Jupiter', mass=0.4, radius=2.0, orbital_period=8000, year_discovered=12)
        db.session.add(exoplanet1)
        db.session.add(exoplanet2)
        db.session.commit()
        exoplanets = Exoplanet.query.all()
        self.assertTrue(exoplanet1 in exoplanets)
        self.assertTrue(exoplanet2 in exoplanets)
        self.assertEqual(len(exoplanets), 2)

    def test_exoplanet2(self):
        exoplanet = Exoplanet(
            id=1, name='Earth', mass=0.2, radius=1.0, orbital_period=5000, year_discovered=0)
        db.session.add(exoplanet)
        db.session.commit()
        db_exoplanet = Exoplanet.query.first()
        self.assertEqual(db_exoplanet.radius, 1.0)
        self.assertEqual(db_exoplanet.year_discovered, 0)

    def test_exoplanet3(self):
        exoplanet = Exoplanet(
            id=1, name='Earth', mass=0.2, radius=1.0, orbital_period=5000, year_discovered=0)
        db.session.add(exoplanet)
        db.session.commit()
        db_exoplanet = Exoplanet.query.first()
        self.assertEqual(db_exoplanet.name, 'Earth')

    def test_exoplanet4(self):
        exoplanet1 = Exoplanet(
            id=1, name='Earth', mass=0.2, radius=1.0, orbital_period=5000, year_discovered=0)
        exoplanet2 = Exoplanet(
            id=2, name='Jupiter', mass=0.4, radius=2.0, orbital_period=8000, year_discovered=12)
        star = Star(id=2, name='Aries', mass=3.0,
                    luminosity=4.0, temperature=7000, radius=3.0)
        star.exoplanets = [exoplanet1, exoplanet2]
        db.session.add(exoplanet1)
        db.session.add(exoplanet2)
        db.session.add(star)
        db.session.commit()
        db_star = Star.query.first()
        self.assertIn(exoplanet1, db_star.exoplanets)
        self.assertIn(exoplanet2, db_star.exoplanets)

    def test_constellation1(self):
        constellation1 = Constellation(
            id=1, name='big dipper', abbrev='big dp', family='arris', meaning='laddle', area=56.54)
        constellation2 = Constellation(
            id=2, name='little dipper', abbrev='small dp', family='arris', meaning='laddle', area=54.56)
        db.session.add(constellation1)
        db.session.add(constellation2)
        db.session.commit()
        constellations = Constellation.query.all()
        self.assertTrue(constellation1 in constellations)
        self.assertTrue(constellation2 in constellations)
        self.assertEqual(len(constellations), 2)

    def test_constellation2(self):
        constellation = Constellation(
            id=1, name='big dipper', abbrev='big dp', family='arris', meaning='laddle', area=56.54)
        db.session.add(constellation)
        db.session.commit()
        db_constellation = Constellation.query.first()
        self.assertEqual(db_constellation.id, 1)
        self.assertEqual(db_constellation.area, 56.54)

    def test_constellation3(self):
        constellation = Constellation(
            id=1, name='big dipper', abbrev='big dp', family='arris', meaning='laddle', area=56.54)
        db.session.add(constellation)
        db.session.commit()
        db_constellation = Constellation.query.first()
        self.assertEqual(db_constellation.name, 'big dipper')

    def test_constellation4(self):
        constellation1 = Constellation(
            id=1, name='big dipper', abbrev='big dp', family='arris', meaning='laddle', area=56.54)
        constellation2 = Constellation(
            id=2, name='little dipper', abbrev='small dp', family='arris', meaning='laddle', area=54.56)
        publication = Publication(
            id=1, title='discovery of new star', year=1986, authors='Carl Sagan, Neil Degrasse Tyson', journal='Harvard Stars', abstract='We found a new star.')
        publication.constellations = [constellation1, constellation2]
        db.session.add(constellation1)
        db.session.add(constellation2)
        db.session.add(publication)
        db_publication = Publication.query.first()
        self.assertIn(constellation1, db_publication.constellations)
        self.assertIn(constellation2, db_publication.constellations)

    def test_publication1(self):
        publication1 = Publication(
            id=1, title='discovery of new star', year=1986, authors='Carl Sagan, Neil Degrasse Tyson', journal='Harvard Stars', abstract='We found a new star.')
        publication2 = Publication(
            id=2, title='discovery of a new fart', year=1995, authors='Rick and Morty', journal='Harvard Astronomy', abstract='We found a new fart.')
        db.session.add(publication1)
        db.session.add(publication2)
        db.session.commit()
        publications = Publication.query.all()
        self.assertTrue(publication1 in publications)
        self.assertTrue(publication2 in publications)
        self.assertEqual(len(publications), 2)

    def test_publication2(self):
        publication = Publication(
            id=1, title='discovery of new star', year=1986, authors='Carl Sagan, Neil Degrasse Tyson', journal='Harvard Stars', abstract='We found a new star.')
        db.session.add(publication)
        db.session.commit()
        db_publication = Publication.query.first()
        self.assertEqual(db_publication.id, 1)
        self.assertEqual(db_publication.year, 1986)

    def test_publication3(self):
        publication = Publication(
            id=1, title='discovery of new star', year=1986, authors='Carl Sagan, Neil Degrasse Tyson', journal='Harvard Stars', abstract='We found a new star.')
        db.session.add(publication)
        db.session.commit()
        db_publication = Publication.query.first()
        self.assertEqual(db_publication.title, 'discovery of new star')

    def test_publication4(self):
        exoplanet1 = Exoplanet(
            id=1, name='Earth', mass=0.2, radius=1.0, orbital_period=5000, year_discovered=0)
        exoplanet2 = Exoplanet(
            id=2, name='Jupiter', mass=0.4, radius=2.0, orbital_period=8000, year_discovered=12)
        publication = Publication(
            id=1, title='discovery of new star', year=1986, authors='Carl Sagan, Neil Degrasse Tyson', journal='Harvard Stars', abstract='We found a new star.')
        publication.exoplanets = [exoplanet1, exoplanet2]
        db.session.add(exoplanet1)
        db.session.add(exoplanet2)
        db.session.commit()
        db_publication = Publication.query.first()
        self.assertIn(exoplanet1, db_publication.exoplanets)
        self.assertIn(exoplanet2, db_publication.exoplanets)
        import os


class ViewsTest(TestCase):

    """ Tests the views """

    def create_app(self):
        return create_app(os.environ.get('APP_ENV', 'dev') + '_test')

    def test_empty_db(self):
        view = self.client.get('/')
        self.assertEqual(view.status, '200 OK')
        self.assertNotEqual(view.data, '')

    def test_get_commits_contents(self):
        commits = views.get_commits()
        for person in commits.items():
            self.assertEqual(len(person), 2)

    def test_get_commits_numbers(self):
        commits = views.get_commits()
        for person, num in commits.items():
            self.assertTrue(num > -1)

    def test_get_issues_size(self):
        issues = views.get_issues()
        self.assertTrue(len(issues) > -1)

    def test_get_issues_contents(self):
        issues = views.get_issues()
        for person in issues.items():
            self.assertEqual(len(person), 2)

    def test_get_issues_numbers(self):
        commits = views.get_issues()
        for person, num in commits.items():
            self.assertTrue(num > -1)

    def test_get_total_commits_size(self):
        commits = views.get_total_commits()
        self.assertTrue(commits > -1)

    def test_get_total_issues_size(self):
        issues = views.get_total_issues()
        self.assertTrue(issues > -1)
