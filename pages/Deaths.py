from page_template import Template

page = Template(measure='Total_fatalities', agg_func='sum')
page.make_page(main_title='Number of fatalities', target_type=None)