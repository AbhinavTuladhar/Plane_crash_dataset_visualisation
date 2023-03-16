from page_template import Template

page = Template(measure='Survival_rate', agg_func='mean')
page.make_page(main_title='Survival rates', target_type=None, treemap_flag=False)