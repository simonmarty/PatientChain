#!/usr/bin/env python

import urllib3
import click


@click.command()
@click.option('--name', prompt='Your name',
              help='The name of the patient')
@click.option('--dob', prompt='Date of birth',
              help='The patient\'s date of birth')
def hello(name, dob):
    click.echo('Name: %s' % name)
    click.echo('Date of Birth: %s' % dob)


if __name__ == '__main__':
    print('Patient File')
    hello()
