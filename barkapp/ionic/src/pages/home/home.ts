import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';
import { BarkService } from '../../services/bark';
import { ListPage } from '../list/list';

@Component({
  selector: 'page-home',
  templateUrl: 'home.html'
})
export class HomePage {
  lastBark: Date;

  constructor(public navCtrl: NavController,
              private barkService: BarkService) {
    this.barkService.last().subscribe((res) => {
      this.lastBark = new Date(res.json());
    });
  }

  clickSeeAllBarks() {
    this.navCtrl.setRoot(ListPage);
  }
}