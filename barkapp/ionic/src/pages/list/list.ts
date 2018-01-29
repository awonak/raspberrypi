import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';

import {BarkService} from '../../services/bark';

@Component({
  selector: 'page-list',
  templateUrl: 'list.html'
})
export class ListPage {
  barks: Date[] = [];
  previousDay: Date;

  constructor(public navCtrl: NavController,
              public navParams: NavParams,
              private barkService: BarkService) {
    this.barkService.all().subscribe((res) => {
      for (let alert of res.json()) {
        this.barks.push(new Date(alert));
      }
    })
  }

}
