const Bleno = require('@abandonware/bleno');

class StaticReadCharacteristic extends Bleno.Characteristic {
	debug = false
	constructor(uuid, description, value, debug = false) {
		super({
			uuid: uuid,
			properties: ['read'],
			value: null,
			descriptors: [
				new Bleno.Descriptor({
					uuid: '2901',
					value: description
				})
			]
		});
		this.debug = debug
		this.uuid = uuid;
		this.description = description;
		this._value = Buffer.isBuffer(value) ? value : new Buffer(value);
	}
	
	onReadRequest(offset, callback) {
		if(this.debug)console.log('OnReadRequest : ' + this.description);
		callback(this.RESULT_SUCCESS, this._value.slice(offset, this._value.length));
	};
}

module.exports = StaticReadCharacteristic;